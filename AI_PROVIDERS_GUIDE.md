# AI Provider Configuration Guide

SlideX supports multiple AI providers for automatic slide tagging. Choose the one that best fits your needs and budget.

## Supported AI Providers

1. **OpenAI** (GPT-3.5/GPT-4) - Recommended for most users
2. **Anthropic** (Claude) - Great alternative with strong reasoning
3. **Roo (Bob)** - Cost-effective option
4. **IBM WatsonX.ai** - Enterprise-grade AI platform
5. **Fallback** - Basic keyword matching (no API key needed)

## Priority Order

The system tries providers in this order:
1. OpenAI
2. Anthropic
3. Roo (Bob)
4. WatsonX
5. Fallback (keyword matching)

Only configure ONE provider - the system will use the first available API key.

---

## Option 1: OpenAI (Recommended)

### Pros
- Most accurate tagging
- Fast response times
- Easy to set up
- $5 free credit for new users

### Cons
- Requires payment method
- ~$0.002 per slide (very affordable)

### Setup

1. **Sign up:** https://platform.openai.com/signup
2. **Add payment method** (required even for free tier)
3. **Create API key:**
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Name it "SlideX"
   - Copy the key (starts with `sk-proj-...`)

4. **Add to .env:**
```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### Cost Estimate
- GPT-3.5-turbo: ~$0.002 per slide
- 1000 slides = ~$2
- Very affordable for most use cases

---

## Option 2: Anthropic (Claude)

### Pros
- Excellent reasoning capabilities
- Good at understanding context
- Competitive pricing

### Cons
- Requires payment method
- Slightly more expensive than OpenAI

### Setup

1. **Sign up:** https://console.anthropic.com/
2. **Add payment method**
3. **Create API key:**
   - Go to Settings → API Keys
   - Click "Create Key"
   - Copy the key (starts with `sk-ant-...`)

4. **Add to .env:**
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Cost Estimate
- Claude Haiku: ~$0.0025 per slide
- 1000 slides = ~$2.50

---

## Option 3: Roo (Bob) API

### Pros
- Cost-effective
- Good for high-volume processing
- Fast response times

### Cons
- May require enterprise account
- Less documentation available

### Setup

1. **Get Roo API access** (contact your Roo representative)
2. **Obtain API key and endpoint URL**

3. **Add to .env:**
```env
ROO_API_KEY=your-roo-api-key-here
ROO_API_URL=https://api.roo.ai/v1
```

### Notes
- Adjust `ROO_API_URL` if your Roo instance uses a different endpoint
- The code uses a chat completion format - verify this matches your Roo API
- Model name is set to `roo-chat` - adjust in `ai_tagger.py` if needed

### Customization

If your Roo API uses different parameters, edit `backend/app/services/ai_tagger.py`:

```python
payload = {
    "model": "your-model-name",  # Change this
    "messages": [...],
    "temperature": 0.3
}
```

---

## Option 4: IBM WatsonX.ai

### Pros
- Enterprise-grade security
- On-premise deployment options
- Compliance-ready
- Multiple model choices

### Cons
- More complex setup
- Requires IBM Cloud account
- Higher cost for small teams

### Setup

1. **Create IBM Cloud account:** https://cloud.ibm.com/
2. **Set up WatsonX.ai project:**
   - Go to WatsonX.ai service
   - Create a new project
   - Note your Project ID

3. **Generate API key:**
   - Go to Manage → Access (IAM)
   - Create API key
   - Copy the key

4. **Add to .env:**
```env
WATSONX_API_KEY=your-watsonx-api-key-here
WATSONX_PROJECT_ID=your-project-id-here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### Available Models
- `ibm/granite-13b-chat-v2` (default)
- `meta-llama/llama-2-70b-chat`
- `google/flan-ul2`

To change the model, edit `backend/app/services/ai_tagger.py`:

```python
payload = {
    "model_id": "your-preferred-model",  # Change this
    ...
}
```

### Regional Endpoints
- US South: `https://us-south.ml.cloud.ibm.com`
- EU Germany: `https://eu-de.ml.cloud.ibm.com`
- Japan Tokyo: `https://jp-tok.ml.cloud.ibm.com`

---

## Option 5: Fallback (No API Key)

### Pros
- Free
- No API key needed
- Works offline
- No external dependencies

### Cons
- Less accurate than AI providers
- Basic keyword matching only
- May miss nuanced categorizations

### Setup

Simply don't configure any API keys. The system will automatically use keyword matching.

### How It Works

The fallback system uses predefined keywords:
- **Client Painpoints:** security, scale, cost, efficiency, integration
- **Client Type:** enterprise, small business, startup
- **Software Type:** CRM, analytics, automation, dashboard
- **Software Function:** report, integrate, dashboard, analyze

You can customize these keywords in `backend/app/services/ai_tagger.py` in the `_generate_basic_tags()` method.

---

## Comparison Table

| Provider | Cost/1000 slides | Setup Time | Accuracy | Best For |
|----------|------------------|------------|----------|----------|
| OpenAI | ~$2 | 5 min | ⭐⭐⭐⭐⭐ | Most users |
| Anthropic | ~$2.50 | 5 min | ⭐⭐⭐⭐⭐ | Alternative to OpenAI |
| Roo | Varies | 10 min | ⭐⭐⭐⭐ | High volume |
| WatsonX | $10+ | 30 min | ⭐⭐⭐⭐ | Enterprise |
| Fallback | Free | 0 min | ⭐⭐⭐ | Testing/offline |

---

## Testing Your Configuration

After configuring your API key, test it:

```bash
cd SlideX/backend
source venv/bin/activate

# Test configuration
python3 -c "
from app.core.config import settings
print('OpenAI:', bool(settings.OPENAI_API_KEY))
print('Anthropic:', bool(settings.ANTHROPIC_API_KEY))
print('Roo:', bool(settings.ROO_API_KEY))
print('WatsonX:', bool(settings.WATSONX_API_KEY))
"
```

Then start the server and upload a test slide to verify tagging works.

---

## Switching Providers

To switch providers:

1. Stop the server
2. Edit `.env` file
3. Comment out old API key (add `#` at start of line)
4. Add new API key
5. Restart server

Example:
```env
# Old provider
# OPENAI_API_KEY=sk-proj-old-key

# New provider
ANTHROPIC_API_KEY=sk-ant-new-key
```

---

## Troubleshooting

### "API key invalid"
- Verify you copied the entire key
- Check for extra spaces
- Ensure key hasn't expired
- Verify billing is set up (OpenAI/Anthropic)

### "Rate limit exceeded"
- You're making too many requests
- Upgrade your API plan
- Add delays between uploads
- Consider switching to a higher-tier plan

### "Model not found" (WatsonX)
- Verify model name is correct
- Check model is available in your region
- Ensure project has access to the model

### Tags are generic/inaccurate
- AI provider might be having issues
- Try a different provider
- Check if slide content is clear
- Consider manual tag review

---

## Cost Optimization Tips

1. **Start with OpenAI free tier** - $5 credit covers ~2500 slides
2. **Use fallback for testing** - No cost during development
3. **Batch uploads** - Process multiple files at once
4. **Cache results** - Don't re-process the same slides
5. **Monitor usage** - Check API dashboards regularly

---

## Security Best Practices

- ✅ Never commit `.env` file to Git
- ✅ Rotate API keys regularly
- ✅ Use separate keys for dev/prod
- ✅ Monitor API usage for anomalies
- ✅ Set spending limits on API accounts
- ✅ Use environment-specific keys

---

## Need Help?

- **OpenAI Issues:** https://help.openai.com/
- **Anthropic Issues:** https://docs.anthropic.com/
- **WatsonX Issues:** https://cloud.ibm.com/docs/watsonxai
- **SlideX Issues:** Open an issue on GitHub

---

**Recommendation:** Start with OpenAI for the best balance of cost, accuracy, and ease of setup. You can always switch later!