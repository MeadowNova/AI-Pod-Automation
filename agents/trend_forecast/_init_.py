from .trend_forecaster import TrendForecaster
#             # Generate prompts from provided keywords
#             optimized_prompts = self.prompt_optimizer.optimize_from_keywords(keywords)
#         else:
#             raise ValueError("No keywords or trend report provided for prompt generation.")
#
#         logger.info(f"Optimized prompts: {optimized_prompts}")
#         return optimized_prompts
#
#         # Generate prompts from trend report
#         if trend_report:
#             trend_report = self.trend_forecaster.generate_trend_report()
#             logger.info(f"Generated trend report: {trend_report}")
#             optimized_prompts = self.prompt_optimizer.optimize_from_trend_report(trend_report)
#         else:
#             raise ValueError("No keywords or trend report provided for prompt generation.")
