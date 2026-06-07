# Product-Specific Keywords Guide

This document outlines the product-specific keywords that have been integrated into SlideX's AI tagging system to improve tagging accuracy for IBM software products.

## Overview

The AI tagging system now recognizes specific IBM products and their associated functions. When slides contain content related to these products, the AI will automatically tag them with the appropriate product name and function tags.

## Supported Products

### 1. Maximo
**Product Category:** Asset Management Software

**Associated Keywords:**
- Asset Management
- Mobile
- Maintenance
- Monitoring
- Visual Inspection
- Service

**Example Tags:**
- `software_type: Maximo`
- `software_function: asset_management`
- `software_function: mobile`
- `software_function: maintenance`
- `software_function: monitoring`
- `software_function: visual_inspection`
- `software_function: service`

---

### 2. Verify
**Product Category:** Identity and Access Management (IAM)

**Associated Keywords:**
- IAM
- Authentication
- Risk
- Delegation
- Consent
- Continuous Audit

**Example Tags:**
- `software_type: Verify`
- `software_function: IAM`
- `software_function: authentication`
- `software_function: risk`
- `software_function: delegation`
- `software_function: consent`
- `software_function: continuous_audit`

---

### 3. Tririga
**Product Category:** Facility and Real Estate Management

**Associated Keywords:**
- Space Management
- Capital Planning
- Lease Management

**Example Tags:**
- `software_type: Tririga`
- `software_function: space_management`
- `software_function: capital_planning`
- `software_function: lease_management`

---

## How It Works

### AI Models
All AI providers (OpenAI, Anthropic, WatsonX, Ollama, Roo) have been updated with product-specific prompts that include:

1. **Product Recognition:** The AI is instructed to identify these specific IBM products when analyzing slide content
2. **Function Mapping:** When a product is detected, the AI maps relevant functions to that product
3. **Keyword Matching:** The AI looks for both explicit product names and related functionality keywords

### Fallback Tagging
The basic keyword matching system (used when no AI is configured) also includes these product-specific keywords:

**Software Keywords:**
- "maximo" → Maximo
- "tririga" → Tririga  
- "verify" → Verify
- "asset", "maintenance", "mobile", "visual inspection" → Maximo
- "space management", "capital planning", "lease" → Tririga
- "iam", "authentication", "identity" → Verify

**Function Keywords:**
- "asset management", "asset_management" → asset_management
- "mobile" → mobile
- "maintenance" → maintenance
- "visual inspection", "visual_inspection" → visual_inspection
- "service" → service
- "iam" → IAM
- "authentication" → authentication
- "risk" → risk
- "delegation" → delegation
- "consent" → consent
- "continuous audit", "continuous_audit" → continuous_audit
- "space management", "space_management" → space_management
- "capital planning", "capital_planning" → capital_planning
- "lease management", "lease_management" → lease_management

## Usage Tips

### For Best Results:
1. **Include product names** in slide titles or content
2. **Use specific function keywords** when describing capabilities
3. **Be consistent** with terminology (e.g., "asset management" vs "asset mgmt")

### Example Slide Content:
```
Title: "Maximo Mobile Solutions"
Content: "Enable field technicians with mobile asset management and visual inspection capabilities"

Expected Tags:
- software_type: Maximo
- software_function: mobile
- software_function: asset_management
- software_function: visual_inspection
```

## Adding New Products

To add new product-specific keywords:

1. Update the AI prompts in `backend/app/services/ai_tagger.py`:
   - `_generate_with_watsonx()` - line ~294
   - `_generate_with_ollama()` - line ~391
   - `_generate_with_openai()` - line ~134
   - `_generate_with_anthropic()` - line ~171
   - `_generate_with_roo()` - line ~203

2. Update the fallback keyword dictionaries in `_generate_basic_tags()` - line ~520:
   - `software_keywords` - Add product name and related terms
   - `function_keywords` - Add product-specific functions

3. Update this documentation with the new product details

## Notes

- Keywords are **case-insensitive** in the fallback system
- AI models may recognize variations and synonyms beyond the exact keywords listed
- Multiple products can be tagged on a single slide if content is relevant to multiple products
- The system prioritizes specific product names over generic categories (e.g., "Maximo" over "CRM")

---

*Last Updated: 2026-06-06*
*Version: 1.0*