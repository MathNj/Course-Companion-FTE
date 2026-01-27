# Install cloudflared - Step by Step Guide

## Method 1: Using winget (Recommended) ⭐

### Step 1: Open PowerShell as Administrator

1. Press `Windows Key`
2. Type: `PowerShell`
3. Right-click on "Windows PowerShell"
4. Select "Run as administrator"
5. Click "Yes" if prompted

### Step 2: Install cloudflared

Run this command in PowerShell:

```powershell
winget install cloudflare.cloudflared
```

**What happens:**
- Downloads cloudflared
- Installs it automatically
- Adds to your PATH
- Shows confirmation when complete

### Step 3: Verify Installation

```powershell
cloudflared --version
```

**Expected output:**
```
cloudflared version 2024.x.x
```

**That's it!** ✅

---

## Method 2: Using Chocolatey (Alternative)

### Step 1: Install Chocolatey (if not already installed)

Open PowerShell as Administrator and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol::Tls12; Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```

### Step 2: Install cloudflared

```powershell
choco install cloudflared
```

### Step 3: Verify

```powershell
cloudflared --version
```

---

## Method 3: Manual Download (If winget doesn't work)

### Step 1: Download

1. Go to: https://github.com/cloudflare/cloudflared/releases/latest
2. Look for: `cloudflared-windows-amd64.msi`
3. Click to download

### Step 2: Install

1. Double-click the downloaded `.msi` file
2. Click "Next" through the installer
3. Use default installation path
4. Click "Install"
5. Wait for completion
6. Click "Finish"

### Step 3: Verify

Open a NEW PowerShell window and run:

```powershell
cloudflared --version
```

---

## After Installation

Once installed, you can use cloudflared from anywhere!

```powershell
# Check version
cloudflared --version

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel --url http://localhost:8000
```

---

## Troubleshooting

### Problem: "cloudflared not recognized"

**Solution:** Close and reopen PowerShell
- The PATH variable needs to refresh after installation

### Problem: "Access denied"

**Solution:** Run PowerShell as Administrator
- Right-click → "Run as administrator"

### Problem: "Can't find winget"

**Solution:** Use Method 2 (Chocolatey) or Method 3 (Manual)

### Problem: Installation fails

**Solution:** Use Method 3 (Manual download)
- Download directly from GitHub
- Install the MSI file

---

## Quick Verification

After installation, open a NEW PowerShell window and test:

```powershell
# Should show version
cloudflared --version

# Should show help
cloudflared --help
```

If both work, installation was successful! ✅

---

## What's Next?

After installing cloudflared:

1. **Login to Cloudflare:**
   ```bash
   cloudflared tunnel login
   ```

2. **Start your backend APIs** (3 terminals)
   ```bash
   python simple_r2_api.py
   python simple_quiz_api.py
   python simple_progress_api.py
   ```

3. **Create tunnels:**
   ```bash
   cloudflared tunnel --url http://localhost:8000
   cloudflared tunnel --url http://localhost:8001
   cloudflared tunnel --url http://localhost:8002
   ```

4. **Copy your URLs!**

---

**Installation Time:** 2-3 minutes

**You're ready to create tunnels!**
