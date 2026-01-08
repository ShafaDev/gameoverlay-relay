# GameOverlay Server - Fly.io Deployment

Complete guide to deploy GameOverlay server on Fly.io

## 📁 Files Included

- `server.py` - Flask-SocketIO server
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration
- `fly.toml` - Fly.io configuration
- `Procfile` - Start command
- `.dockerignore` - Ignored files

## 🚀 Quick Deployment Steps

### 1️⃣ Install Fly.io CLI

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Mac/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

### 2️⃣ Login to Fly.io

```bash
fly auth login
```

### 3️⃣ Upload to GitHub

1. Create new repository on GitHub
2. Upload all server files:
   - server.py
   - requirements.txt
   - Dockerfile
   - fly.toml
   - Procfile
   - .dockerignore

3. Push to GitHub

### 4️⃣ Deploy from GitHub

**Option A: Direct Deploy**
```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Create fly app
fly apps create your-app-name

# Deploy
fly deploy
```

**Option B: Connect GitHub to Fly.io**
1. Go to Fly.io dashboard
2. Click "Create App"
3. Connect GitHub repository
4. Select your repository
5. Click "Deploy"

### 5️⃣ Configure App Name

Edit `fly.toml` and change:
```toml
app = "your-app-name"  # Change this!
```

### 6️⃣ Launch App

```bash
fly launch
```

Follow prompts:
- Choose app name
- Select region (closest to you)
- Don't add database
- Deploy now: Yes

### 7️⃣ Check Status

```bash
fly status
```

### 8️⃣ Get Your URL

```bash
fly info
```

Your server URL will be:
```
https://your-app-name.fly.dev
```

## ⚙️ Configuration

### Change App Name

In `fly.toml`:
```toml
app = "gameoverlay-server"  # Your custom name
```

### Change Region

In `fly.toml`:
```toml
primary_region = "iad"  # Change to your region
```

Available regions:
- `iad` - US East (Ashburn)
- `lax` - US West (Los Angeles)
- `fra` - Europe (Frankfurt)
- `sin` - Asia (Singapore)
- `syd` - Australia (Sydney)

### Increase Memory (if needed)

In `fly.toml`:
```toml
[[vm]]
  memory_mb = 512  # Increase from 256
```

## 🔧 Useful Commands

### View Logs
```bash
fly logs
```

### Restart App
```bash
fly apps restart your-app-name
```

### Check App Status
```bash
fly status
```

### Open App in Browser
```bash
fly open
```

### Scale App
```bash
fly scale count 1
```

### Destroy App
```bash
fly apps destroy your-app-name
```

## 📝 Update Your Client

After deployment, update GameOverlay.py:

```python
DEFAULT_SETTINGS = {
    "server_url": "https://your-app-name.fly.dev",
    # ... rest of settings
}
```

## 🌐 Testing Your Server

1. Open browser to: `https://your-app-name.fly.dev`
2. Should see:
```json
{
  "status": "running",
  "service": "GameOverlay Server",
  "version": "1.0",
  "active_rooms": 0
}
```

3. Health check: `https://your-app-name.fly.dev/health`

## 🐛 Troubleshooting

### App Won't Start
```bash
fly logs
```
Check logs for errors

### Connection Issues
1. Check if app is running:
```bash
fly status
```

2. Restart app:
```bash
fly apps restart your-app-name
```

### Update App
```bash
fly deploy
```

### Check App Info
```bash
fly info
```

## 💰 Pricing

Fly.io Free Tier includes:
- 3 shared-cpu-1x VMs with 256MB RAM
- 160GB/month bandwidth
- Perfect for GameOverlay!

## 📱 Alternative Deployment Options

### Option 1: Railway
1. Go to railway.app
2. Connect GitHub
3. Deploy from repo
4. Get URL

### Option 2: Render
1. Go to render.com
2. New Web Service
3. Connect GitHub repo
4. Deploy

### Option 3: Heroku
1. Go to heroku.com
2. Create new app
3. Connect GitHub
4. Deploy

## 🎯 Complete Workflow

```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Clone from GitHub
git clone https://github.com/YOUR_USERNAME/gameoverlay-server.git
cd gameoverlay-server

# 4. Deploy
fly launch

# 5. Get URL
fly info

# 6. Test in browser
# Visit: https://your-app-name.fly.dev

# 7. Update client with new URL
# Edit GameOverlay.py server_url

# 8. Done! 🎉
```

## 📞 Support

If deployment fails:
1. Check fly logs: `fly logs`
2. Verify all files uploaded to GitHub
3. Check fly.toml app name
4. Try different region
5. Check Fly.io status page

## ✅ Deployment Checklist

- [ ] Fly.io CLI installed
- [ ] Logged in to Fly.io
- [ ] Files uploaded to GitHub
- [ ] fly.toml app name changed
- [ ] App deployed successfully
- [ ] URL obtained
- [ ] Server tested in browser
- [ ] Client updated with new URL
- [ ] Chat tested successfully

## 🎉 Success!

Your GameOverlay server is now running on Fly.io!

URL: `https://your-app-name.fly.dev`

Update this in GameOverlay.py settings and start chatting! 🚀
