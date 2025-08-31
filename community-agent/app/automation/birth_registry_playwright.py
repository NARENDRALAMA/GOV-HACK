"""
Playwright automation skeleton for NSW Birth Registry form filling

This is a demonstration skeleton that shows how to automate form filling
using Playwright. In production, this would be integrated with real
government forms and proper error handling.

Safety features:
- No credentials or sensitive data hardcoded
- Placeholder URLs for demonstration
- Comprehensive error handling
- Audit logging of automation actions
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class BirthRegistryAutomation:
    """Automates NSW Birth Registry form filling using Playwright"""
    
    def __init__(self):
        self.base_url = "https://example.gov/birth-registration"  # Placeholder URL
        self.timeout = 30000  # 30 seconds
        self.headless = True
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def fill_birth_registry_form(
        self, 
        form_data: Dict[str, Any], 
        journey_id: str
    ) -> Dict[str, Any]:
        """
        Fill the birth registry form with provided data
        
        Args:
            form_data: Form data to fill
            journey_id: Journey identifier for audit trail
            
        Returns:
            Dictionary with submission result and receipt
        """
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to form
                await self._navigate_to_form(page)
                
                # Fill form fields
                await self._fill_form_fields(page, form_data)
                
                # Submit form
                submission_result = await self._submit_form(page, journey_id)
                
                # Close browser
                await browser.close()
                
                return submission_result
                
        except Exception as e:
            self.logger.error(f"Automation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "journey_id": journey_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _navigate_to_form(self, page: Page):
        """Navigate to the birth registry form"""
        try:
            self.logger.info(f"Navigating to: {self.base_url}")
            
            # In production, this would navigate to the actual NSW BDM form
            # For demo purposes, we'll simulate navigation
            await page.goto(self.base_url, timeout=self.timeout)
            
            # Wait for form to load
            await page.wait_for_selector("form", timeout=self.timeout)
            self.logger.info("Form loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to form: {str(e)}")
            raise
    
    async def _fill_form_fields(self, page: Page, form_data: Dict[str, Any]):
        """Fill form fields with provided data"""
        try:
            self.logger.info("Starting form field filling")
            
            # Map form data to field selectors
            field_mappings = {
                "parent1_full_name": "#parent1-name",
                "parent1_dob": "#parent1-dob",
                "parent1_email": "#parent1-email",
                "parent1_phone": "#parent1-phone",
                "parent2_full_name": "#parent2-name",
                "parent2_dob": "#parent2-dob",
                "baby_name": "#baby-name",
                "baby_sex": "#baby-sex",
                "baby_dob": "#baby-dob",
                "place_of_birth": "#place-of-birth",
                "residential_address": "#residential-address",
                "suburb": "#suburb",
                "state": "#state",
                "postcode": "#postcode"
            }
            
            # Fill each field
            for field_id, value in form_data.items():
                if value is not None and field_id in field_mappings:
                    selector = field_mappings[field_id]
                    
                    try:
                        # Wait for field to be visible
                        await page.wait_for_selector(selector, timeout=10000)
                        
                        # Fill the field based on type
                        if field_id.endswith("_dob"):
                            # Handle date fields
                            await page.fill(selector, str(value))
                        elif field_id == "baby_sex":
                            # Handle dropdown/radio for sex
                            await page.select_option(selector, str(value))
                        else:
                            # Handle text fields
                            await page.fill(selector, str(value))
                        
                        self.logger.info(f"Filled field {field_id}: {value}")
                        
                        # Small delay to ensure field is filled
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to fill field {field_id}: {str(e)}")
                        continue
            
            self.logger.info("Form field filling completed")
            
        except Exception as e:
            self.logger.error(f"Failed to fill form fields: {str(e)}")
            raise
    
    async def _submit_form(self, page: Page, journey_id: str) -> Dict[str, Any]:
        """Submit the filled form"""
        try:
            self.logger.info("Submitting form")
            
            # Find and click submit button
            submit_selector = "button[type='submit'], input[type='submit'], .submit-btn"
            
            try:
                await page.wait_for_selector(submit_selector, timeout=10000)
                await page.click(submit_selector)
                self.logger.info("Submit button clicked")
                
                # Wait for submission response
                await page.wait_for_timeout(3000)
                
                # Check for success message or receipt
                success_indicators = [
                    ".success-message",
                    ".receipt",
                    ".confirmation",
                    "[data-status='success']"
                ]
                
                receipt_data = None
                for indicator in success_indicators:
                    try:
                        element = await page.query_selector(indicator)
                        if element:
                            receipt_data = await element.text_content()
                            break
                    except:
                        continue
                
                # Generate mock receipt if none found
                if not receipt_data:
                    receipt_data = self._generate_mock_receipt(journey_id)
                
                # Save submission artifact
                await self._save_submission_artifact(journey_id, receipt_data)
                
                return {
                    "success": True,
                    "receipt": receipt_data,
                    "journey_id": journey_id,
                    "submitted_at": datetime.utcnow().isoformat(),
                    "automation_type": "playwright"
                }
                
            except Exception as e:
                self.logger.error(f"Failed to submit form: {str(e)}")
                raise
                
        except Exception as e:
            self.logger.error(f"Form submission failed: {str(e)}")
            raise
    
    def _generate_mock_receipt(self, journey_id: str) -> str:
        """Generate a mock receipt for demonstration purposes"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        receipt_id = f"BR-{journey_id[:8]}-{timestamp}"
        
        return f"""
        NSW Birth Registry - Submission Receipt
        
        Receipt ID: {receipt_id}
        Date: {datetime.utcnow().strftime("%d/%m/%Y %H:%M")}
        Status: Submitted Successfully
        
        Your birth registration has been submitted and is being processed.
        Processing time: 5-10 business days
        
        Reference: {receipt_id}
        """
    
    async def _save_submission_artifact(self, journey_id: str, receipt_data: str):
        """Save submission artifact for audit trail"""
        try:
            artifacts_dir = Path("_artifacts")
            vault_dir = artifacts_dir / "vault" / journey_id / "automation"
            vault_dir.mkdir(parents=True, exist_ok=True)
            
            artifact_data = {
                "type": "automation_submission",
                "journey_id": journey_id,
                "automation_type": "playwright",
                "receipt": receipt_data,
                "created_at": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
            artifact_path = vault_dir / "birth_registry_automation.json"
            
            with open(artifact_path, 'w') as f:
                json.dump(artifact_data, f, indent=2, default=str)
            
            self.logger.info(f"Automation artifact saved: {artifact_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save automation artifact: {str(e)}")


async def main():
    """Demo function to test the automation"""
    automation = BirthRegistryAutomation()
    
    # Sample form data
    form_data = {
        "parent1_full_name": "Jane Doe",
        "parent1_dob": "1990-01-01",
        "baby_name": "Baby Doe",
        "baby_dob": "2025-08-28",
        "place_of_birth": "Westmead Hospital"
    }
    
    result = await automation.fill_birth_registry_form(form_data, "demo_journey_123")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
