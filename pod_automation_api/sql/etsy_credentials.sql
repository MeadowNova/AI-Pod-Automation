-- Create etsy_credentials table
CREATE TABLE IF NOT EXISTS etsy_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    api_key TEXT NOT NULL,
    api_secret TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    shop_id TEXT,
    token_expiry TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    UNIQUE(user_id)
);

-- Add RLS policies
ALTER TABLE etsy_credentials ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own credentials
CREATE POLICY "Users can view their own etsy credentials"
    ON etsy_credentials
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own credentials
CREATE POLICY "Users can insert their own etsy credentials"
    ON etsy_credentials
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own credentials
CREATE POLICY "Users can update their own etsy credentials"
    ON etsy_credentials
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own credentials
CREATE POLICY "Users can delete their own etsy credentials"
    ON etsy_credentials
    FOR DELETE
    USING (auth.uid() = user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_etsy_credentials_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update updated_at timestamp
CREATE TRIGGER update_etsy_credentials_updated_at
BEFORE UPDATE ON etsy_credentials
FOR EACH ROW
EXECUTE FUNCTION update_etsy_credentials_updated_at();

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS etsy_credentials_user_id_idx ON etsy_credentials(user_id);
