"""
FastAPI backend for POD Automation System.
Provides a RESTful API for interacting with the system.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Query, Path as PathParam, Body, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

# Import utilities
from pod_automation.config.logging_config import get_logger
from pod_automation.config.config import get_config
from pod_automation.core.database import get_database
from pod_automation.core.workflow import get_workflow_manager
from pod_automation.core.system import PODAutomationSystem

# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="POD Automation API",
    description="API for POD Automation System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system
system = PODAutomationSystem()

# Initialize database
db = get_database()

# Initialize workflow manager
workflow_manager = get_workflow_manager()


# Define models
class APIResponse(BaseModel):
    """API response model."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class DesignRequest(BaseModel):
    """Design generation request model."""
    keyword: str
    num_designs: int = Field(default=1, ge=1, le=10)
    style: Optional[str] = None
    colors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ListingRequest(BaseModel):
    """Listing optimization request model."""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    product_type: str
    keyword: str
    metadata: Optional[Dict[str, Any]] = None


class MockupRequest(BaseModel):
    """Mockup generation request model."""
    design_id: int
    product_types: List[str]
    metadata: Optional[Dict[str, Any]] = None


class PublishRequest(BaseModel):
    """Publish request model."""
    design_id: int
    title: str
    description: str
    product_types: List[str]
    tags: List[str]
    platforms: List[str] = Field(default=["printify", "etsy"])
    metadata: Optional[Dict[str, Any]] = None


class WorkflowRequest(BaseModel):
    """Workflow request model."""
    name: str
    description: Optional[str] = None
    keyword: str
    product_types: List[str]
    publish: bool = False
    metadata: Optional[Dict[str, Any]] = None


# Define API routes
@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint."""
    return APIResponse(
        success=True,
        message="POD Automation API",
        data={"version": "1.0.0"}
    )


@app.get("/status", response_model=APIResponse)
async def get_status():
    """Get system status."""
    try:
        # Validate API connections
        validation = system.validate_api_connections()
        
        return APIResponse(
            success=True,
            message="System status",
            data={
                "api_connections": validation,
                "database": db.conn is not None,
                "workflow_manager": workflow_manager is not None
            }
        )
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Design endpoints
@app.post("/designs", response_model=APIResponse)
async def create_design(request: DesignRequest):
    """Create a design."""
    try:
        # Generate designs
        designs = system.design_pipeline.run_pipeline(
            analyze_trends=False,
            base_keyword=request.keyword,
            num_designs=request.num_designs,
            style=request.style,
            colors=request.colors
        )
        
        # Save designs to database
        design_ids = []
        
        for design_path in designs:
            design_name = os.path.basename(design_path)
            
            design_data = {
                "name": design_name,
                "path": design_path,
                "keyword": request.keyword,
                "prompt": system.design_pipeline.last_prompt,
                "metadata": json.dumps(request.metadata or {})
            }
            
            design_id = db.create("designs", design_data)
            design_ids.append(design_id)
        
        return APIResponse(
            success=True,
            message=f"Created {len(designs)} designs",
            data={
                "design_ids": design_ids,
                "design_paths": designs
            }
        )
    except Exception as e:
        logger.error(f"Error creating design: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/designs", response_model=APIResponse)
async def list_designs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    keyword: Optional[str] = Query(None)
):
    """List designs."""
    try:
        # Build query
        query = "SELECT * FROM designs"
        params = []
        
        if keyword:
            query += " WHERE keyword LIKE ?"
            params.append(f"%{keyword}%")
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        designs = db.query(query, tuple(params))
        
        return APIResponse(
            success=True,
            message=f"Found {len(designs)} designs",
            data={"designs": designs}
        )
    except Exception as e:
        logger.error(f"Error listing designs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/designs/{design_id}", response_model=APIResponse)
async def get_design(design_id: int = PathParam(..., ge=1)):
    """Get a design by ID."""
    try:
        # Get design from database
        design = db.read("designs", design_id)
        
        if design:
            return APIResponse(
                success=True,
                message=f"Found design with ID {design_id}",
                data={"design": design}
            )
        else:
            raise HTTPException(status_code=404, detail=f"Design with ID {design_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting design: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/designs/{design_id}/image")
async def get_design_image(design_id: int = PathParam(..., ge=1)):
    """Get a design image by ID."""
    try:
        # Get design from database
        design = db.read("designs", design_id)
        
        if design and os.path.exists(design["path"]):
            return FileResponse(design["path"])
        else:
            raise HTTPException(status_code=404, detail=f"Design image with ID {design_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting design image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Listing endpoints
@app.post("/listings/optimize", response_model=APIResponse)
async def optimize_listing(request: ListingRequest):
    """Optimize a listing."""
    try:
        # Optimize listing
        optimized_listing = system.seo_optimizer.optimize_listing(
            request.keyword,
            request.product_type,
            title=request.title,
            description=request.description,
            tags=request.tags
        )
        
        return APIResponse(
            success=True,
            message="Listing optimized successfully",
            data={"listing": optimized_listing}
        )
    except Exception as e:
        logger.error(f"Error optimizing listing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Mockup endpoints
@app.post("/mockups", response_model=APIResponse)
async def create_mockups(request: MockupRequest):
    """Create mockups for a design."""
    try:
        # Get design from database
        design = db.read("designs", request.design_id)
        
        if not design:
            raise HTTPException(status_code=404, detail=f"Design with ID {request.design_id} not found")
        
        # Create mockups
        mockups = system.mockup_generator.create_mockups_for_design(
            design["path"],
            product_types=request.product_types
        )
        
        # Save mockups to database
        mockup_ids = []
        
        for product_type, mockup_path in mockups.items():
            mockup_data = {
                "design_id": request.design_id,
                "product_type": product_type,
                "path": mockup_path,
                "metadata": json.dumps(request.metadata or {})
            }
            
            mockup_id = db.create("mockups", mockup_data)
            mockup_ids.append(mockup_id)
        
        return APIResponse(
            success=True,
            message=f"Created {len(mockups)} mockups",
            data={
                "mockup_ids": mockup_ids,
                "mockups": mockups
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating mockups: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mockups", response_model=APIResponse)
async def list_mockups(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    design_id: Optional[int] = Query(None),
    product_type: Optional[str] = Query(None)
):
    """List mockups."""
    try:
        # Build query
        query = "SELECT * FROM mockups"
        params = []
        
        conditions = []
        
        if design_id:
            conditions.append("design_id = ?")
            params.append(design_id)
        
        if product_type:
            conditions.append("product_type = ?")
            params.append(product_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        mockups = db.query(query, tuple(params))
        
        return APIResponse(
            success=True,
            message=f"Found {len(mockups)} mockups",
            data={"mockups": mockups}
        )
    except Exception as e:
        logger.error(f"Error listing mockups: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mockups/{mockup_id}", response_model=APIResponse)
async def get_mockup(mockup_id: int = PathParam(..., ge=1)):
    """Get a mockup by ID."""
    try:
        # Get mockup from database
        mockup = db.read("mockups", mockup_id)
        
        if mockup:
            return APIResponse(
                success=True,
                message=f"Found mockup with ID {mockup_id}",
                data={"mockup": mockup}
            )
        else:
            raise HTTPException(status_code=404, detail=f"Mockup with ID {mockup_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mockup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mockups/{mockup_id}/image")
async def get_mockup_image(mockup_id: int = PathParam(..., ge=1)):
    """Get a mockup image by ID."""
    try:
        # Get mockup from database
        mockup = db.read("mockups", mockup_id)
        
        if mockup and os.path.exists(mockup["path"]):
            return FileResponse(mockup["path"])
        else:
            raise HTTPException(status_code=404, detail=f"Mockup image with ID {mockup_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mockup image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Publishing endpoints
@app.post("/publish", response_model=APIResponse)
async def publish_product(request: PublishRequest):
    """Publish a product."""
    try:
        # Get design from database
        design = db.read("designs", request.design_id)
        
        if not design:
            raise HTTPException(status_code=404, detail=f"Design with ID {request.design_id} not found")
        
        # Get mockups for design
        mockups_query = "SELECT * FROM mockups WHERE design_id = ?"
        mockups = db.query(mockups_query, (request.design_id,))
        
        if not mockups:
            raise HTTPException(status_code=404, detail=f"No mockups found for design with ID {request.design_id}")
        
        # Organize mockups by product type
        mockup_paths = {}
        for mockup in mockups:
            if mockup["product_type"] in request.product_types:
                mockup_paths[mockup["product_type"]] = mockup["path"]
        
        # Publish product
        published = system.publishing_agent.publish_design(
            design_path=design["path"],
            title=request.title,
            description=request.description,
            product_types=request.product_types,
            tags=request.tags,
            mockup_paths=mockup_paths,
            platforms=request.platforms
        )
        
        if published:
            return APIResponse(
                success=True,
                message="Product published successfully",
                data={"published": published}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to publish product")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products", response_model=APIResponse)
async def list_products(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    design_id: Optional[int] = Query(None),
    product_type: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """List products."""
    try:
        # Build query
        query = "SELECT * FROM products"
        params = []
        
        conditions = []
        
        if design_id:
            conditions.append("design_id = ?")
            params.append(design_id)
        
        if product_type:
            conditions.append("product_type = ?")
            params.append(product_type)
        
        if platform:
            conditions.append("platform = ?")
            params.append(platform)
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        products = db.query(query, tuple(params))
        
        return APIResponse(
            success=True,
            message=f"Found {len(products)} products",
            data={"products": products}
        )
    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{product_id}", response_model=APIResponse)
async def get_product(product_id: int = PathParam(..., ge=1)):
    """Get a product by ID."""
    try:
        # Get product from database
        product = db.read("products", product_id)
        
        if product:
            # Get tags for product
            tags_query = "SELECT tag FROM tags WHERE product_id = ?"
            tags_result = db.query(tags_query, (product_id,))
            
            tags = [tag["tag"] for tag in tags_result]
            product["tags"] = tags
            
            return APIResponse(
                success=True,
                message=f"Found product with ID {product_id}",
                data={"product": product}
            )
        else:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Workflow endpoints
@app.post("/workflows", response_model=APIResponse)
async def create_workflow(request: WorkflowRequest):
    """Create and execute a workflow."""
    try:
        # Create workflow
        workflow = workflow_manager.create_workflow(
            name=request.name,
            description=request.description or f"Workflow for {request.keyword}",
            context={
                "keyword": request.keyword,
                "product_types": request.product_types,
                "publish": request.publish,
                "metadata": request.metadata
            }
        )
        
        # Add tasks to workflow
        from pod_automation.core.workflow import Task
        
        # Task 1: Trend Analysis
        workflow.add_task(Task(
            name="trend_analysis",
            func=system.trend_forecaster.run_trend_analysis,
            args=[[request.keyword]]
        ))
        
        # Task 2: Design Generation
        workflow.add_task(Task(
            name="design_generation",
            func=system.design_pipeline.run_pipeline,
            kwargs={
                "analyze_trends": False,
                "base_keyword": request.keyword,
                "num_designs": 3
            },
            dependencies=["trend_analysis"]
        ))
        
        # Task 3: Mockup Creation
        workflow.add_task(Task(
            name="mockup_creation",
            func=lambda designs, product_types, context: {
                design_path: system.mockup_generator.create_mockups_for_design(
                    design_path,
                    product_types=product_types
                ) for design_path in designs
            },
            args=[workflow.context.get("design_generation"), request.product_types],
            dependencies=["design_generation"]
        ))
        
        # Task 4: SEO Optimization
        workflow.add_task(Task(
            name="seo_optimization",
            func=system.seo_optimizer.optimize_listing,
            args=[request.keyword, request.product_types[0]],
            dependencies=["trend_analysis"]
        ))
        
        # Task 5: Publishing (if requested)
        if request.publish:
            workflow.add_task(Task(
                name="publishing",
                func=lambda designs, mockups, listing, product_types, context: [
                    system.publishing_agent.publish_design(
                        design_path=design_path,
                        title=listing["title"],
                        description=listing["description"],
                        product_types=product_types,
                        tags=listing["tags"],
                        mockup_paths=mockup_paths
                    ) for design_path, mockup_paths in mockups.items() if mockup_paths
                ],
                args=[
                    workflow.context.get("design_generation"),
                    workflow.context.get("mockup_creation"),
                    workflow.context.get("seo_optimization"),
                    request.product_types
                ],
                dependencies=["mockup_creation", "seo_optimization"]
            ))
        
        # Execute workflow in a separate thread
        import threading
        
        thread = threading.Thread(
            target=workflow.execute
        )
        thread.start()
        
        return APIResponse(
            success=True,
            message=f"Workflow '{request.name}' created and started",
            data={"workflow_id": workflow.id}
        )
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows", response_model=APIResponse)
async def list_workflows(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List workflows."""
    try:
        # Get workflows from database
        workflows = workflow_manager.list_workflows(limit=limit)
        
        return APIResponse(
            success=True,
            message=f"Found {len(workflows)} workflows",
            data={"workflows": workflows}
        )
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows/{workflow_id}", response_model=APIResponse)
async def get_workflow(workflow_id: int = PathParam(..., ge=1)):
    """Get a workflow by ID."""
    try:
        # Get workflow from database
        workflow = workflow_manager.get_workflow_status(workflow_id)
        
        if workflow:
            return APIResponse(
                success=True,
                message=f"Found workflow with ID {workflow_id}",
                data={"workflow": workflow}
            )
        else:
            raise HTTPException(status_code=404, detail=f"Workflow with ID {workflow_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def start_api(host="0.0.0.0", port=8000):
    """Start the FastAPI server."""
    import uvicorn
    
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_api()