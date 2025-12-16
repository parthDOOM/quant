# Visual Studio Build Tools Installation Guide

## Step 1: Download Build Tools

1. **Open this link in your browser:**
   https://visualstudio.microsoft.com/downloads/

2. **Scroll down to "All Downloads"**

3. **Find "Tools for Visual Studio 2022"**

4. **Download: "Build Tools for Visual Studio 2022"**
   - File size: ~3-4 MB (installer only)
   - Actual installation: ~7 GB

## Step 2: Run the Installer

1. **Run the downloaded file:** `vs_BuildTools.exe`

2. **Wait for the Visual Studio Installer to load** (takes 30-60 seconds)

3. **Select Workload:** "Desktop development with C++"
   - Check the box for "Desktop development with C++"
   
4. **Verify Individual Components** (should be auto-selected):
   - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools (Latest)
   - ✅ Windows 11 SDK (or Windows 10 SDK)
   - ✅ C++ CMake tools for Windows
   - ✅ C++ core features

5. **Click "Install"**
   - Installation time: 15-30 minutes
   - Downloads ~6-7 GB

## Step 3: Verify Installation

After installation completes:

1. **Close PowerShell windows**

2. **Open "Developer PowerShell for VS 2022"**
   - Search in Start Menu: "Developer PowerShell"
   - Or use regular PowerShell (the paths should be set)

3. **Run verification command:**
   ```powershell
   cl
   ```
   
   **Expected output:**
   ```
   Microsoft (R) C/C++ Optimizing Compiler Version 19.XX.XXXXX for x64
   Copyright (C) Microsoft Corporation.  All rights reserved.
   
   usage: cl [ option... ] filename... [ /link linkoption... ]
   ```

4. **Check CMake can find compiler:**
   ```powershell
   cmake --version
   ```

## Step 4: Return Here

Once you see the compiler version, come back to this chat and let me know:
- ✅ "Compiler installed successfully" 
- Or any errors you encountered

---

## Troubleshooting

### If `cl` command not found:
1. Make sure you're using "Developer PowerShell for VS 2022"
2. Or add to PATH manually (I'll help with this)

### If installation fails:
1. Check disk space (need ~10 GB free)
2. Try downloading again
3. Let me know the exact error message

---

**Take your time!** Installation takes 15-30 minutes depending on your internet speed. 

While it's installing, you can grab a coffee ☕ - I'll be here when you're ready for the next step!
