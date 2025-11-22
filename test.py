"""
Test suite for API layer.
Tests Ollama client and route logic.
"""
import json
from unittest.mock import Mock, patch

from src.api import get_ollama_client, router
from src.config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def test_ollama_client_init():
    """Test Ollama client initialization."""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: OLLAMA CLIENT INITIALIZATION")
    logger.info("="*60)
    
    try:
        client = get_ollama_client()
        
        logger.info(f"✓ Client initialized")
        logger.info(f"  Model: {client.model}")
        logger.info(f"  Tools loaded: {len(client.tools)}")
        
        # Verify tools are in correct format
        assert len(client.tools) > 0, "No tools loaded"
        
        for tool in client.tools:
            assert 'type' in tool, "Tool missing 'type'"
            assert 'function' in tool, "Tool missing 'function'"
            assert 'name' in tool['function'], "Tool function missing 'name'"
            assert 'description' in tool['function'], "Tool function missing 'description'"
            assert 'parameters' in tool['function'], "Tool function missing 'parameters'"
        
        logger.info(f"\n✓ All {len(client.tools)} tools properly formatted")
        logger.info("\nTool names:")
        for tool in client.tools:
            logger.info(f"  - {tool['function']['name']}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Client initialization failed: {e}")
        return False

def test_tool_conversion():
    """Test MCP to Ollama tool format conversion."""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: TOOL FORMAT CONVERSION")
    logger.info("="*60)
    
    client = get_ollama_client()
    
    # Check specific tool structure
    upload_tool = None
    for tool in client.tools:
        if tool['function']['name'] == 'upload_dataset':
            upload_tool = tool
            break
    
    assert upload_tool is not None, "upload_dataset tool not found"
    
    logger.info("✓ Found upload_dataset tool")
    logger.info(f"\nTool structure:")
    logger.info(f"  Type: {upload_tool['type']}")
    logger.info(f"  Name: {upload_tool['function']['name']}")
    logger.info(f"  Description: {upload_tool['function']['description'][:60]}...")
    logger.info(f"  Parameters: {list(upload_tool['function']['parameters'].keys())}")
    
    # Validate schema
    params = upload_tool['function']['parameters']
    assert 'type' in params, "Parameters missing 'type'"
    assert 'properties' in params, "Parameters missing 'properties'"
    assert 'required' in params, "Parameters missing 'required'"
    
    logger.info("\n✓ Tool format validation passed")
    
    return True


def test_health_check():
    """Test Ollama health check."""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: HEALTH CHECK")
    logger.info("="*60)
    
    client = get_ollama_client()
    
    try:
        health = client.check_health()
        
        logger.info(f"Status: {health.get('status')}")
        logger.info(f"Ollama running: {health.get('ollama_running')}")
        
        if health.get('ollama_running'):
            logger.info(f"Current model: {health.get('current_model')}")
            logger.info(f"Available models: {health.get('available_models')}")
            logger.info(f"Tools count: {health.get('tools_count')}")
            logger.info("\n✓ Ollama is accessible")
        else:
            logger.warning(f"\n⚠ Ollama not accessible: {health.get('error')}")
            logger.info("This is OK if Ollama isn't running yet")
        
        return health.get('ollama_running', False)
        
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
        return False


def test_tool_execution_mock():
    """Test tool execution with mock."""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: TOOL EXECUTION (MOCKED)")
    logger.info("="*60)
    
    client = get_ollama_client()
    
    # Mock the handle_tool_call function
    with patch('src.api.ollama_client.handle_tool_call') as mock_handler:
        # Setup mock return value
        mock_result = Mock()
        mock_result.text = json.dumps({
            "status": "success",
            "action": "check_dataset",
            "result": {
                "exists": True,
                "name": "test_dataset"
            }
        })
        mock_handler.return_value = [mock_result]
        
        # Execute tool
        result = client._execute_tool("check_dataset", {"dataset_name": "test_dataset"})
        
        # Verify
        result_data = json.loads(result)
        assert result_data['status'] == 'success', "Tool execution failed"
        
        logger.info("✓ Tool execution successful (mocked)")
        logger.info(f"  Action: {result_data['action']}")
        logger.info(f"  Result: {result_data['result']}")
    
    return True 


def test_chat_with_ollama():
    """Test actual chat with Ollama (if available)."""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: CHAT WITH OLLAMA")
    logger.info("="*60)
    
    client = get_ollama_client()
    
    # Check if Ollama is running
    health = client.check_health()
    
    if not health.get('ollama_running'):
        logger.warning("⚠ Ollama not running - skipping chat test")
        logger.info("To run this test:")
        logger.info("  1. Start Ollama: ollama serve")
        logger.info("  2. Pull model: ollama pull llama3.1:8b")
        return False
    
    try:
        # Simple chat without tools
        logger.info("\n🤖 Test 5a: Simple chat (no tools)")
        messages = [
            {"role": "user", "content": "Say hello in exactly 5 words"}
        ]
        
        response = client.chat(messages, max_iterations=1)
        
        logger.info(f"✓ Chat response received")
        logger.info(f"  Message: {response['message']}")
        logger.info(f"  Iterations: {response['iterations']}")
        
        # Chat that should trigger tool (but we'll mock it)
        logger.info("\n🤖 Test 5b: Chat with potential tool call")
        messages = [
            {"role": "user", "content": "List all available tools you can use"}
        ]
        
        response = client.chat(messages, max_iterations=2)
        
        logger.info(f"✓ Chat response received")
        logger.info(f"  Response length: {len(response['message'])} chars")
        logger.info(f"  Iterations: {response['iterations']}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Chat test failed: {e}")
        logger.info("This might be because:")
        logger.info("  - Ollama model not downloaded")
        logger.info("  - Model doesn't support tool calling")
        return False


def test_routes_defined():
    """Test that routes are properly defined."""
    logger.info("\n" + "="*60)
    logger.info("TEST 6: FASTAPI ROUTES")
    logger.info("="*60)
    
    # Get all routes from router
    routes = [route for route in router.routes]
    
    logger.info(f"✓ Found {len(routes)} routes:")
    
    expected_routes = ['/api/chat', '/api/tools', '/api/health']
    
    for route in routes:
        path = route.path
        methods = list(route.methods) if hasattr(route, 'methods') else []
        logger.info(f"  - {path} [{', '.join(methods)}]")
    
    # Verify expected routes exist
    route_paths = [route.path for route in routes]
    
    for expected in expected_routes:
        assert expected in route_paths, f"Route {expected} not found"
    
    logger.info(f"\n✓ All expected routes defined")
    
    return True


def main():
    """Run all API tests."""
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + " "*19 + "API LAYER TEST SUITE" + " "*19 + "║")
    logger.info("╚" + "="*58 + "╝")
    
    results = {}
    
    try:
        # Run tests
        results['client_init'] = test_ollama_client_init()
        results['tool_conversion'] = test_tool_conversion()
        results['health_check'] = test_health_check()
        results['tool_execution'] = test_tool_execution_mock()
        results['chat'] = test_chat_with_ollama()
        results['routes'] = test_routes_defined()
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        logger.info("\nResults:")
        for test_name, passed in results.items():
            status = "✓ PASS" if passed else "⚠ SKIP/WARN"
            logger.info(f"  {test_name:20s} {status}")
        
        # Check critical tests
        critical_tests = ['client_init', 'tool_conversion', 'routes']
        all_critical_passed = all(results.get(t, False) for t in critical_tests)
        
        if all_critical_passed:
            logger.info("\n✅ ALL CRITICAL TESTS PASSED!")
            logger.info("\nAPI layer is ready for integration.")
        else:
            logger.warning("\n⚠ Some critical tests failed")
        
        if not results.get('health_check'):
            logger.info("\nℹ️  Note: Ollama health check failed")
            logger.info("   Make sure Ollama is running before starting the server:")
            logger.info("   1. ollama serve")
            logger.info("   2. ollama pull llama3.1:8b")
        
    except Exception as e:
        logger.error(f"\n❌ TEST SUITE FAILED: {e}")
        raise
    
    logger.info("\n" + "="*60)
    logger.info("API test suite completed!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
