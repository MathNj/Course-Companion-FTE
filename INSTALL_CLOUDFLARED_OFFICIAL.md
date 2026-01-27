# Install cloudflared - Official 2024 Methods

## Based on official Cloudflare documentation

---

## 🚀 **Method 1: Winget (Official Recommended)** ⭐

### Step 1: Open PowerShell as Administrator

1. Press **Windows Key**
2. Type: **`PowerShell`**
3. Right-click **"Windows PowerShell"**
4. Select **"Run as administrator"**
5. Click **"Yes"** when prompted

### Step 2: Install with explicit package ID

Run this command:

```powershell
winget install --id Cloudflare.cloudflared --accept-package-agreements --accept-source-agreements
```

**What this does:**
- Installs the latest cloudflared version
- Auto-accepts all license agreements
- Adds to your system PATH
- Places in `C:\Program Files\cloudflared\`

### Step 3: Close and Reopen PowerShell

Close all PowerShell windows and open a fresh one.

### Step 4: Verify Installation

```powershell
cloudflared.exe --version
```

**Expected output:**
```
cloudflared version 2024.x.x
```

---

## 📥 **Method 2: Direct Download (Alternative)**

### Step 1: Download from GitHub

**Official download page:**
https://github.com/cloudflare/cloudflared/releases/latest

### Step 2: Choose Windows version

Download: **`cloudflared-windows-amd64.msi`** (recommended)

### Step 3: Install

1. Double-click the downloaded `.msi` file
2. Click **"Next"** through the installer
3. Use **default** settings
4. Click **"Install"**
5. Wait for completion
6. Click **"Finish"**

### Step 4: Verify

Open PowerShell and test:
```powershell
cloudflared.exe --version
```

---

## 🍫 **Method 3: Chocolatey (If you have it)**

### Step 1: Open PowerShell as Administrator

### Step 2: Install
```powershell
choco install cloudflared -y
```

### Step 3: Verify
```powershell
cloudflared.exe --version
```

---

## ⚠️ **Important for Windows Users**

### **Use `cloudflared.exe` not `cloudflared`**

On Windows, you need to use the `.exe` extension:

```powershell
# ✅ CORRECT
cloudflared.exe --version

# ❌ WRONG (won't work)
cloudflared --version
```

### **Installation Location**

cloudflared will be installed to:
```
C:\Program Files\cloudflared\
```

### **PATH Configuration**

The installer should add cloudflared to your PATH automatically.

---

## 🔍 **After Installation**

### **Test in NEW PowerShell window:**

```powershell
# Check version
cloudflared.exe --version

# Show help
cloudflared.exe --help
```

### **If not in PATH:**

```powershell
# Add to current session
$env:Path += ";C:\Program Files\cloudflared"

# Then test
cloudflared.exe --version
```

---

## 🎯 **Next Steps After Installation**

Once installed:

### **1. Login to Cloudflare**
```powershell
cloudflared.exe tunnel login
```

This opens a browser - login and authorize.

### **2. Create tunnels**
```powershell
# Terminal 1
cloudflared.exe tunnel --url http://localhost:8000

# Terminal 2
cloudflared.exe tunnel --url http://localhost:8001

# Terminal 3
cloudflared.exe tunnel --url http://localhost:8002
```

Each will give you a URL like:
```
https://abc123def456.trycloudflare.com
```

---

## 📚 **Sources**

Official documentation:
- Cloudflare Developers Portal: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/
- Cloudflare GitHub: https://github.com/cloudflare/cloudflared
- Chocolatey Package: https://community.chocolatey.org/packages/cloudflared

---

## ✅ **Installation Checklist**

Follow these steps:

- [ ] Open PowerShell as Administrator
- [ ] Run: `winget install --id Cloudflare.cloudflared --accept-package-agreements --accept-source-agreements`
- [ ] Wait for "Successfully installed" message
- [ ] Close and reopen PowerShell
- [ ] Run: `cloudflared.exe --version`
- [ ] See version output

**Expected time:** 3-5 minutes

---

## 🆘 **Troubleshooting**

### **Problem: "command not recognized"**
**Solution:** Use `cloudflared.exe` instead of `cloudflared`

### **Problem: "access denied"**
**Solution:** Run PowerShell as Administrator

### **Problem: "package not found"**
**Solution:** Use Method 2 (direct download)

### **Problem: "version not found"**
**Solution:** Add to PATH manually or use full path: `"C:\Program Files\cloudflared\cloudflared.exe"`

---

## 🎯 **Quick Start Commands**

```powershell
# Install (run as Admin)
winget install --id Cloudflare.cloudflared --accept-package-agreements --accept-source-agreements

# Verify (in NEW PowerShell window)
cloudflared.exe --version

# Login
cloudflared.exe tunnel login

# Create tunnel
cloudflared.exe tunnel --url http://localhost:8000
```

---

**Choose Method 1 (Winget) - it's the official recommended method!**

Let me know once you've installed it successfully! 🚀
