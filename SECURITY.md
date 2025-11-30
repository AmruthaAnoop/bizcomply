# Security Guidelines

## 🔐 API Key Management

### ✅ **Secure Implementation**

This project follows security best practices for API key management:

#### **1. Environment Variables Only**
- All API keys are stored as environment variables
- No hardcoded API keys in source code
- Configuration centralized in `config/config.py`

#### **2. Git Protection**
- `.env` files are excluded via `.gitignore`
- Only `.env.example` with placeholder values is tracked
- Prevents accidental API key exposure

#### **3. Centralized Configuration**
```python
# config/config.py - Secure pattern
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
```

### 🚫 **What NOT to Do**

❌ **NEVER** commit actual API keys:
```python
# WRONG - Don't do this!
api_key = "sk-1234567890abcdef..."
```

❌ **NEVER** hardcode credentials in code:
```python
# WRONG - Don't do this!
OPENAI_API_KEY = "sk-actual-key-here"
```

### ✅ **What TO Do**

✅ **Always** use environment variables:
```python
# CORRECT - Use this pattern
from config.config import OPENAI_API_KEY
```

✅ **Always** use `.env.example` for templates:
```bash
# .env.example - Safe to commit
OPENAI_API_KEY=your_openai_api_key_here
```

✅ **Always** keep actual `.env` file local:
```bash
# .env - Never commit
OPENAI_API_KEY=sk-actual-key-here
```

### 🔧 **Setup Instructions**

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the actual file:**
   ```bash
   # .env - Add your real keys
   OPENAI_API_KEY=sk-your-actual-key
   GROQ_API_KEY=gsk_your-actual-key
   ```

3. **Verify it's ignored:**
   ```bash
   git status  # Should NOT show .env
   ```

### 🛡️ **Security Checklist**

- [ ] `.env` is in `.gitignore`
- [ ] No hardcoded keys in source code
- [ ] All keys use `os.getenv()` or config imports
- [ ] Only `.env.example` is committed
- [ ] Environment variables are set in deployment
- [ ] Keys are rotated regularly
- [ ] Access is limited to necessary personnel

### 🚨 **If Keys Are Exposed**

If you accidentally commit API keys:

1. **Immediately rotate the keys** in your provider dashboard
2. **Remove from Git history:**
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push to clean history:**
   ```bash
   git push origin --force --all
   ```
4. **Update your local `.env`** with new keys

### 📞 **Report Security Issues**

If you discover security vulnerabilities:
- Email: security@bizcomply.com
- Private GitHub issue
- Do NOT open public issues

---

**Remember**: API keys are like passwords - treat them with the same care! 🔐
