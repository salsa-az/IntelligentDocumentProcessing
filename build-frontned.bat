@echo off
cd frontend
npm install
npm run build
if exist "..\endpoint\dist" rmdir /s /q "..\endpoint\dist"
move dist "..\endpoint\dist"
cd ..