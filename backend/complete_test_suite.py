import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json
import os
from datetime import datetime

# Import your app components (adjust imports based on your project structure)
from main import app  # Your FastAPI app
from app.api.v1.chat import get_firebase_token, get_current_user
from app.core.agent import run_agent, get_session_history
from app.core.crews.blog_crew import create_blog_post_crew
from app.services.firebase_service import (
    save_message_to_firestore, 
    get_conversations_from_firestore,
    verify_firebase_token
)
from app.services.vector_db_service import add_text_to_vector_db, search_user_memory

# Test Configuration
class TestConfig:
    TEST_USER_ID = "test_user_123"
    TEST_SESSION_ID = "test_session_456"
    TEST_TOKEN = "test_firebase_token"
    MOCK_USER_DATA = {"uid": TEST_USER_ID, "email": "test@example.com"}

@pytest.fixture
def test_client():
    """Create a test client for FastAPI app"""
    return TestClient(app)

@pytest.fixture
def mock_firebase_token():
    """Mock Firebase token verification"""
    with patch('app.routes.chat_routes.verify_firebase_token') as mock:
        mock.return_value = TestConfig.MOCK_USER_DATA
        yield mock

@pytest.fixture
def mock_vector_db():
    """Mock vector database operations"""
    with patch('app.services.vector_db_service.add_text_to_vector_db') as add_mock, \
         patch('app.services.vector_db_service.search_user_memory') as search_mock:
        search_mock.return_value = ["Previous conversation context"]
        yield add_mock, search_mock

@pytest.fixture
def mock_firestore():
    """Mock Firestore operations"""
    with patch('app.services.firebase_service.save_message_to_firestore') as save_mock, \
         patch('app.services.firebase_service.get_conversations_from_firestore') as get_mock:
        get_mock.return_value = [
            {
                "session_id": TestConfig.TEST_SESSION_ID,
                "sender": "user",
                "text": "Hello",
                "timestamp": "2025-01-01T12:00:00"
            }
        ]
        yield save_mock, get_mock

@pytest.fixture
def mock_groq_llm():
    """Mock Groq LLM responses"""
    with patch('app.core.agent.get_groq_llm') as mock:
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Mocked AI response")
        mock.return_value = mock_llm
        yield mock

class TestAuthentication:
    """Test Firebase authentication and token handling"""
    
    def test_get_firebase_token_success(self):
        """Test successful token extraction from Authorization header"""
        from fastapi import Request
        
        # Mock request with proper Authorization header
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
        
        result = get_firebase_token(mock_request)
        assert result == TestConfig.TEST_TOKEN

    def test_get_firebase_token_missing_header(self):
        """Test token extraction fails when Authorization header is missing"""
        from fastapi import Request
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        
        with pytest.raises(HTTPException) as exc_info:
            get_firebase_token(mock_request)
        
        assert exc_info.value.status_code == 401
        assert "Authorization header missing" in str(exc_info.value.detail)

    def test_get_firebase_token_invalid_format(self):
        """Test token extraction fails with invalid header format"""
        from fastapi import Request
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "InvalidFormat token123"}
        
        with pytest.raises(HTTPException) as exc_info:
            get_firebase_token(mock_request)
        
        assert exc_info.value.status_code == 401
        assert "Invalid authorization header format" in str(exc_info.value.detail)

    def test_get_current_user_success(self, mock_firebase_token):
        """Test successful user data retrieval"""
        result = get_current_user(TestConfig.TEST_TOKEN)
        assert result == TestConfig.MOCK_USER_DATA
        mock_firebase_token.assert_called_once_with(TestConfig.TEST_TOKEN)

    def test_get_current_user_invalid_token(self):
        """Test user authentication fails with invalid token"""
        with patch('app.routes.chat_routes.verify_firebase_token') as mock:
            mock.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                get_current_user("invalid_token")
            
            assert exc_info.value.status_code == 401
            assert "Invalid or expired authentication token" in str(exc_info.value.detail)

class TestChatEndpoints:
    """Test chat-related API endpoints"""
    
    @patch('app.routes.chat_routes.run_agent')
    def test_handle_chat_success(self, mock_run_agent, test_client, mock_firebase_token, 
                                 mock_vector_db, mock_firestore):
        """Test successful chat interaction"""
        # Mock agent response
        mock_run_agent.return_value = {"output": "AI response to user query"}
        
        # Test request
        headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
        payload = {
            "user_input": "Hello, how are you?",
            "session_id": TestConfig.TEST_SESSION_ID
        }
        
        response = test_client.post("/chat", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["output"] == "AI response to user query"
        
        # Verify vector DB and Firestore operations were called
        add_mock, search_mock = mock_vector_db
        save_mock, get_mock = mock_firestore
        
        assert add_mock.call_count == 2  # User message + AI response
        assert save_mock.call_count == 2  # User message + AI response

    def test_handle_chat_unauthorized(self, test_client):
        """Test chat endpoint returns 401 without proper authentication"""
        payload = {"user_input": "Hello", "session_id": TestConfig.TEST_SESSION_ID}
        
        response = test_client.post("/chat", json=payload)
        
        assert response.status_code == 401

    @patch('app.routes.chat_routes.create_blog_post_crew')
    def test_invoke_crew_success(self, mock_crew, test_client, mock_firebase_token):
        """Test successful crew invocation"""
        mock_crew.return_value = "Generated blog post content"
        
        headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
        payload = {"topic": "AI in Healthcare"}
        
        response = test_client.post("/chat/invoke_crew", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Generated blog post content"
        mock_crew.assert_called_once_with("AI in Healthcare")

    def test_invoke_crew_missing_topic(self, test_client, mock_firebase_token):
        """Test crew invocation fails without topic"""
        headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
        payload = {"topic": ""}
        
        response = test_client.post("/chat/invoke_crew", json=payload, headers=headers)
        
        assert response.status_code == 400
        assert "topic is required" in response.json()["detail"]

class TestChatHistory:
    """Test chat history management"""
    
    def test_get_chat_history_success(self, test_client, mock_firebase_token, mock_firestore):
        """Test successful chat history retrieval"""
        headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
        
        response = test_client.get("/chat/history", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert len(data["history"]) > 0

    def test_get_chat_history_empty(self, test_client, mock_firebase_token):
        """Test chat history retrieval with no history"""
        with patch('app.routes.chat_routes.get_conversations_from_firestore') as mock:
            mock.return_value = []
            
            headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
            response = test_client.get("/chat/history", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["history"] == []

    def test_delete_chat_history_success(self, test_client, mock_firebase_token):
        """Test successful chat history deletion"""
        with patch('app.routes.chat_routes.delete_conversation_from_firestore') as mock:
            mock.return_value = True
            
            headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
            response = test_client.delete("/chat/history", headers=headers)
            
            assert response.status_code == 200
            assert "deleted successfully" in response.json()["message"]

    def test_delete_single_session_success(self, test_client, mock_firebase_token):
        """Test successful single session deletion"""
        with patch('app.routes.chat_routes.delete_single_session_from_firestore') as mock:
            mock.return_value = True
            
            headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
            session_id = TestConfig.TEST_SESSION_ID
            
            response = test_client.delete(f"/chat/history/{session_id}", headers=headers)
            
            assert response.status_code == 200
            assert f"Session {session_id} deleted successfully" in response.json()["message"]

class TestAgentFunctionality:
    """Test AI agent core functionality"""
    
    @patch('app.core.agent.agent')
    @patch('app.core.agent.llm')
    def test_run_agent_success(self, mock_llm, mock_agent):
        """Test successful agent execution"""
        # Mock agent executor
        with patch('app.core.agent.AgentExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor.invoke.return_value = {"output": "Agent response"}
            mock_executor_class.return_value = mock_executor
            
            # Mock memory search
            with patch('app.core.agent.search_user_memory') as mock_search:
                mock_search.return_value = ["Previous context"]
                
                result = run_agent("Hello", TestConfig.TEST_SESSION_ID, TestConfig.TEST_USER_ID)
                
                assert result["output"] == "Agent response"
                mock_executor.invoke.assert_called_once()

    @patch('app.core.agent.agent', None)
    @patch('app.core.agent.llm', None)
    def test_run_agent_not_initialized(self):
        """Test agent behavior when not properly initialized"""
        result = run_agent("Hello", TestConfig.TEST_SESSION_ID, TestConfig.TEST_USER_ID)
        
        assert "Agent not initialized" in result["output"]
        assert "GROQ_API_KEY" in result["output"]

    @patch('app.core.agent.AgentExecutor')
    @patch('app.core.agent.llm')
    def test_run_agent_fallback_to_llm(self, mock_llm, mock_executor_class):
        """Test fallback to direct LLM call when agent fails"""
        # Mock agent executor to raise exception
        mock_executor = Mock()
        mock_executor.invoke.side_effect = Exception("Agent failed")
        mock_executor_class.return_value = mock_executor
        
        # Mock LLM fallback
        mock_llm.invoke.return_value = Mock(content="Fallback LLM response")
        
        with patch('app.core.agent.agent', Mock()):
            result = run_agent("Hello", TestConfig.TEST_SESSION_ID, TestConfig.TEST_USER_ID)
            
            assert result["output"] == "Fallback LLM response"
            mock_llm.invoke.assert_called_once_with("Hello")

class TestVectorDatabase:
    """Test vector database operations"""
    
    @patch('app.services.vector_db_service.client')
    @patch('app.services.vector_db_service.embedding_model')
    def test_add_text_to_vector_db_success(self, mock_embedding, mock_client):
        """Test successful text addition to vector database"""
        # Mock embedding model
        mock_embedding.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        
        # Mock ChromaDB collection
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        add_text_to_vector_db(
            TestConfig.TEST_USER_ID, 
            "Test message", 
            {"sender": "user", "session_id": TestConfig.TEST_SESSION_ID}
        )
        
        mock_client.get_or_create_collection.assert_called_once_with(
            name=f"user_{TestConfig.TEST_USER_ID}"
        )
        mock_collection.add.assert_called_once()

    @patch('app.services.vector_db_service.client')
    @patch('app.services.vector_db_service.embedding_model')
    def test_search_user_memory_success(self, mock_embedding, mock_client):
        """Test successful memory search"""
        # Mock embedding model
        mock_embedding.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        
        # Mock ChromaDB collection
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [["Previous conversation", "Another memory"]]
        }
        mock_client.get_collection.return_value = mock_collection
        
        result = search_user_memory(TestConfig.TEST_USER_ID, "search query")
        
        assert result == ["Previous conversation", "Another memory"]
        mock_client.get_collection.assert_called_once_with(
            name=f"user_{TestConfig.TEST_USER_ID}"
        )

    @patch('app.services.vector_db_service.client')
    def test_search_user_memory_no_collection(self, mock_client):
        """Test memory search when user collection doesn't exist"""
        mock_client.get_collection.side_effect = Exception("Collection not found")
        
        result = search_user_memory(TestConfig.TEST_USER_ID, "search query")
        
        assert result == []

class TestFirebaseService:
    """Test Firebase/Firestore operations"""
    
    @patch('app.services.firebase_service.get_db_client')
    def test_save_message_to_firestore_success(self, mock_db_client):
        """Test successful message saving to Firestore"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.collection.return_value.document.return_value.collection.return_value = mock_collection
        mock_db_client.return_value = mock_db
        
        save_message_to_firestore(
            TestConfig.TEST_USER_ID, 
            TestConfig.TEST_SESSION_ID, 
            "user", 
            "Hello"
        )
        
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args[0][0]
        assert call_args['session_id'] == TestConfig.TEST_SESSION_ID
        assert call_args['sender'] == "user"
        assert call_args['text'] == "Hello"

    @patch('app.services.firebase_service.get_db_client')
    def test_get_conversations_success(self, mock_db_client):
        """Test successful conversation retrieval"""
        # Mock Firestore query results
        mock_doc = Mock()
        mock_doc.to_dict.return_value = {
            'session_id': TestConfig.TEST_SESSION_ID,
            'sender': 'user',
            'text': 'Hello',
            'timestamp': datetime.now()
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_doc]
        
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value.collection.return_value.order_by.return_value = mock_query
        mock_db_client.return_value = mock_db
        
        result = get_conversations_from_firestore(TestConfig.TEST_USER_ID)
        
        assert len(result) == 1
        assert result[0]['session_id'] == TestConfig.TEST_SESSION_ID

class TestBlogCrew:
    """Test CrewAI blog generation functionality"""
    
    @patch('app.core.crews.blog_crew.get_groq_llm')
    @patch('app.core.crews.blog_crew.get_available_search_tools')
    def test_create_blog_post_crew_success(self, mock_tools, mock_llm):
        """Test successful blog post generation"""
        # Mock tools and LLM
        mock_tools.return_value = [Mock()]
        mock_llm.return_value = Mock()
        
        # Mock Crew execution
        with patch('app.core.crews.blog_crew.Crew') as mock_crew_class:
            mock_crew = Mock()
            mock_crew.kickoff.return_value = "Generated blog post content"
            mock_crew_class.return_value = mock_crew
            
            result = create_blog_post_crew("AI in Healthcare")
            
            assert result == "Generated blog post content"
            mock_crew.kickoff.assert_called_once()

    @patch('app.core.crews.blog_crew.get_groq_llm')
    def test_create_blog_post_crew_error_handling(self, mock_llm):
        """Test blog crew error handling"""
        mock_llm.side_effect = Exception("LLM initialization failed")
        
        result = create_blog_post_crew("AI in Healthcare")
        
        assert "overwhelmed at the moment" in result

class TestAPIKeyValidation:
    """Test API key validation and environment setup"""
    
    def test_missing_groq_api_key(self):
        """Test behavior when GROQ_API_KEY is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('app.core.agent.get_groq_llm') as mock:
                mock.side_effect = Exception("GROQ_API_KEY not found in .env file.")
                
                result = run_agent("Hello", TestConfig.TEST_SESSION_ID, TestConfig.TEST_USER_ID)
                
                assert "Agent not initialized" in result["output"]

class TestErrorHandling:
    """Test various error scenarios"""
    
    def test_invalid_json_payload(self, test_client, mock_firebase_token):
        """Test handling of invalid JSON payloads"""
        headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
        
        response = test_client.post("/chat", data="invalid json", headers=headers)
        
        assert response.status_code == 422

    def test_database_connection_failure(self, test_client, mock_firebase_token):
        """Test handling of database connection failures"""
        with patch('app.services.firebase_service.get_conversations_from_firestore') as mock:
            mock.return_value = None  # Simulates database failure
            
            headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
            response = test_client.get("/chat/history", headers=headers)
            
            assert response.status_code == 500

class TestPerformance:
    """Test performance-related scenarios"""
    
    @pytest.mark.asyncio
    async def test_concurrent_chat_requests(self, test_client, mock_firebase_token):
        """Test handling of concurrent chat requests"""
        with patch('app.routes.chat_routes.run_agent') as mock_agent:
            mock_agent.return_value = {"output": "Concurrent response"}
            
            headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
            payload = {"user_input": "Hello", "session_id": TestConfig.TEST_SESSION_ID}
            
            # Simulate concurrent requests
            tasks = []
            for i in range(5):
                task = asyncio.create_task(
                    asyncio.to_thread(
                        test_client.post, "/chat", json=payload, headers=headers
                    )
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200

class TestSecurityValidation:
    """Test security-related functionality"""
    
    def test_sql_injection_attempt(self, test_client, mock_firebase_token, mock_vector_db, mock_firestore):
        """Test handling of potential SQL injection attempts"""
        with patch('app.routes.chat_routes.run_agent') as mock_agent:
            mock_agent.return_value = {"output": "Safe response"}
            
            headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
            malicious_input = "'; DROP TABLE users; --"
            payload = {"user_input": malicious_input, "session_id": TestConfig.TEST_SESSION_ID}
            
            response = test_client.post("/chat", json=payload, headers=headers)
            
            assert response.status_code == 200
            # Verify the malicious input was passed to the agent (should be sanitized there)
            mock_agent.assert_called_once()

    def test_oversized_payload(self, test_client, mock_firebase_token):
        """Test handling of oversized payloads"""
        headers = {"Authorization": f"Bearer {TestConfig.TEST_TOKEN}"}
        large_input = "A" * 10000  # Very large input
        payload = {"user_input": large_input, "session_id": TestConfig.TEST_SESSION_ID}
        
        response = test_client.post("/chat", json=payload, headers=headers)
        
        # Should either succeed or return appropriate error, but not crash
        assert response.status_code in [200, 413, 422]

# Test Configuration and Utilities
class TestUtilities:
    """Test utility functions and configurations"""
    
    def test_session_history_management(self):
        """Test session history storage and retrieval"""
        from app.core.agent import SESSION_STORE
        
        # Clear any existing sessions
        SESSION_STORE.clear()
        
        history1 = get_session_history("session1")
        history2 = get_session_history("session2")
        
        # Should be different instances
        assert history1 is not history2
        
        # Should persist the same instance for the same session
        history1_again = get_session_history("session1")
        assert history1 is history1_again

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",  # Verbose output
        "--tb=short",  # Shorter traceback format
        "--durations=10"  # Show 10 slowest tests
    ])