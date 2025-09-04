---
applyTo: "src/**/*.{html,css,js}"
---

# Frontend Development Instructions

## Tauri Frontend Guidelines

- Keep frontend code minimal and focused on UI
- Use vanilla JavaScript or minimal frameworks
- Communicate with Rust backend via Tauri commands
- Handle loading states and errors gracefully

## UI/UX Principles

- Follow modern desktop application patterns
- Ensure responsive design for different window sizes
- Implement proper keyboard navigation
- Use consistent styling throughout

## Tauri Integration

- Use `invoke()` for calling Rust commands
- Listen to Tauri events for backend updates
- Handle command errors appropriately
- Implement proper loading indicators

## Performance

- Minimize JavaScript bundle size
- Use efficient DOM manipulation
- Implement virtual scrolling for large lists
- Optimize CSS for smooth animations
