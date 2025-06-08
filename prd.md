Implement a FastAPI backend service for an intelligent construction site agent based on the following architectural design:

**Project Requirements:**
- FastAPI backend with LangChain integration
- Qwen3 API from Bailian (阿里云百炼) as the LLM
- Function calling capabilities for construction site queries
- PostgreSQL database with Redis caching
- Streaming response functionality
- Agent that can handle questions like "工地上多少工人在场" and make appropriate function calls

**Implementation Tasks:**
1. Set up the project structure as designed in the architecture
2. Implement the database models and schema (PostgreSQL)
3. Create the Qwen3 client integration with Bailian API
4. Implement LangChain agent with function calling tools
5. Create FastAPI endpoints for chat and streaming
6. Implement business services (workers, equipment, progress)
7. Add repository layer for data access
8. Create function tools for construction site queries
9. Set up streaming response functionality
10. Add configuration management and environment setup
11. Create Docker setup for deployment
12. Add basic error handling and logging
