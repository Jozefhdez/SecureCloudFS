#!/bin/bash
# Script to help with Railway deployment setup

echo "=== Railway Deployment Setup ==="
echo ""

echo "1. Copy your OCI Private Key content:"
echo "   Run this command and copy the output:"
echo "   cat /Users/jozefhdez/.oci/oci_api_key.pem"
echo ""

echo "2. Go to Railway and add these environment variables:"
echo ""
echo "SUPABASE_URL=$(grep SUPABASE_URL .env | cut -d '=' -f2)"
echo "SUPABASE_API_KEY=$(grep SUPABASE_API_KEY .env | cut -d '=' -f2)"
echo "OCI_USER_OCID=$(grep OCI_USER_OCID .env | cut -d '=' -f2)"
echo "OCI_FINGERPRINT=$(grep OCI_FINGERPRINT .env | cut -d '=' -f2)"
echo "OCI_TENANCY_OCID=$(grep OCI_TENANCY_OCID .env | cut -d '=' -f2)"
echo "OCI_REGION=$(grep OCI_REGION .env | cut -d '=' -f2)"
echo "OCI_NAMESPACE=$(grep OCI_NAMESPACE .env | cut -d '=' -f2)"
echo "OCI_BUCKET_NAME=$(grep OCI_BUCKET_NAME .env | cut -d '=' -f2)"
echo "LOG_LEVEL=$(grep LOG_LEVEL .env | cut -d '=' -f2)"
echo ""
echo "OCI_PRIVATE_KEY=<paste the content from step 1 here>"
echo ""

echo "3. Railway will automatically deploy your backend API"
echo "4. After deployment, copy the Railway URL (e.g., https://your-app.railway.app)"
echo "5. Use that URL for your frontend deployment on Vercel"
echo ""

echo "Need help? Check the README.md for detailed instructions."
