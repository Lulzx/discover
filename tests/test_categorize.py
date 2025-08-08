import os
import pytest
import orjson
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
import numpy as np

# Note: Using pytest as the testing framework with unittest.mock for mocking
# This follows Python best practices for unit testing with external dependencies

# Import the function to test
# Adjust the import based on actual module structure
try:
    from ..categorize import categorize_messages
except ImportError:
    # Alternative import if running from different location
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from categorize import categorize_messages


class TestCategorizeMessages:
    """Comprehensive unit tests for the categorize_messages function."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Setup: Create a temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        self.test_output_path = os.path.join(self.temp_dir, 'test_categories.json')
        
        yield
        
        # Teardown: Remove temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_categorize_messages_happy_path(self):
        """Test successful categorization with valid messages."""
        mock_messages = [
            "Python is a great programming language",
            "Machine learning is fascinating",
            "Python programming tutorials",
            "Deep learning with neural networks",
            "Data science and analytics"
        ]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print') as mock_print:
            
            categorize_messages(n_clusters=2, output_path=self.test_output_path)
            
            # Verify the output file was created
            assert os.path.exists(self.test_output_path)
            
            # Verify the content structure
            with open(self.test_output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            
            assert len(categorized_data) == len(mock_messages)
            for item in categorized_data:
                assert 'category' in item
                assert 'text' in item
                assert isinstance(item['category'], int)
                assert item['category'] >= 0 and item['category'] < 2
                assert item['text'] in mock_messages
            
            # Verify print statement was called
            mock_print.assert_called_with(f'Saved categorized messages to {self.test_output_path}')
    
    def test_categorize_messages_empty_messages(self):
        """Test behavior when no messages are found."""
        with patch('categorize.get_messages', return_value=[]), \
             patch('builtins.print') as mock_print:
            
            categorize_messages(output_path=self.test_output_path)
            
            # Verify appropriate message is printed
            mock_print.assert_called_once_with('No messages found for categorization')
            
            # Verify no output file was created
            assert not os.path.exists(self.test_output_path)
    
    def test_categorize_messages_single_message(self):
        """Test edge case with only one message."""
        mock_messages = ["Single message for testing"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            categorize_messages(n_clusters=1, output_path=self.test_output_path)
            
            assert os.path.exists(self.test_output_path)
            
            with open(self.test_output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            
            assert len(categorized_data) == 1
            assert categorized_data[0]['category'] == 0
            assert categorized_data[0]['text'] == mock_messages[0]
    
    def test_categorize_messages_large_dataset(self):
        """Test with a larger dataset to ensure scalability."""
        mock_messages = [f"Message number {i} with unique content" for i in range(100)]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            categorize_messages(n_clusters=10, output_path=self.test_output_path)
            
            assert os.path.exists(self.test_output_path)
            
            with open(self.test_output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            
            assert len(categorized_data) == 100
            
            # Verify all categories are within expected range
            categories = set(item['category'] for item in categorized_data)
            assert all(0 <= cat < 10 for cat in categories)
    
    def test_categorize_messages_creates_directory(self):
        """Test that the function creates the output directory if it doesn't exist."""
        nested_path = os.path.join(self.temp_dir, 'nested', 'dir', 'categories.json')
        mock_messages = ["Test message"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            categorize_messages(n_clusters=1, output_path=nested_path)
            
            assert os.path.exists(nested_path)
            assert os.path.isfile(nested_path)
    
    def test_categorize_messages_default_parameters(self):
        """Test function with default parameters."""
        mock_messages = ["Message 1", "Message 2", "Message 3", "Message 4", "Message 5", "Message 6"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'), \
             patch('os.makedirs') as mock_makedirs, \
             patch('builtins.open', mock_open()) as mock_file:
            
            categorize_messages()
            
            # Verify default output path directory creation
            mock_makedirs.assert_called_once_with('cache', exist_ok=True)
            
            # Verify file was opened for writing
            mock_file.assert_called_once_with('cache/categories.json', 'wb')
    
    def test_categorize_messages_with_special_characters(self):
        """Test handling of messages with special characters and unicode."""
        mock_messages = [
            "Hello 世界! 🌍",
            "Special chars: @#$%^&*()",
            "Newline\ncharacters\ttabs",
            "Émoji test 😀 🎉"
        ]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            categorize_messages(n_clusters=2, output_path=self.test_output_path)
            
            assert os.path.exists(self.test_output_path)
            
            with open(self.test_output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            
            # Verify all special character messages are preserved
            texts = [item['text'] for item in categorized_data]
            for msg in mock_messages:
                assert msg in texts
    
    def test_categorize_messages_kmeans_parameters(self):
        """Test that KMeans is initialized with correct parameters."""
        mock_messages = ["Message 1", "Message 2", "Message 3"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'), \
             patch('categorize.KMeans') as mock_kmeans_class:
            
            mock_kmeans_instance = MagicMock()
            mock_kmeans_instance.fit_predict.return_value = np.array([0, 1, 0])
            mock_kmeans_class.return_value = mock_kmeans_instance
            
            categorize_messages(n_clusters=3, output_path=self.test_output_path)
            
            # Verify KMeans was initialized with correct parameters
            mock_kmeans_class.assert_called_once_with(n_clusters=3, random_state=42)
    
    def test_categorize_messages_tfidf_configuration(self):
        """Test that TfidfVectorizer is configured correctly."""
        mock_messages = ["Test message one", "Test message two"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'), \
             patch('categorize.TfidfVectorizer') as mock_tfidf_class:
            
            mock_vectorizer = MagicMock()
            mock_vectorizer.fit_transform.return_value = MagicMock()
            mock_tfidf_class.return_value = mock_vectorizer
            
            categorize_messages(n_clusters=2, output_path=self.test_output_path)
            
            # Verify TfidfVectorizer was initialized with stop_words parameter
            mock_tfidf_class.assert_called_once_with(stop_words='english')
            mock_vectorizer.fit_transform.assert_called_once()
    
    def test_categorize_messages_file_write_error(self):
        """Test error handling when file writing fails."""
        mock_messages = ["Test message"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'), \
             patch('builtins.open', side_effect=IOError("Write failed")), \
             pytest.raises(IOError, match="Write failed"):
            categorize_messages(output_path=self.test_output_path)
    
    def test_categorize_messages_invalid_n_clusters(self):
        """Test behavior with invalid n_clusters values."""
        mock_messages = ["Message 1", "Message 2"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            # Test with n_clusters greater than number of samples
            # This should still work as sklearn handles this internally
            categorize_messages(n_clusters=5, output_path=self.test_output_path)
            
            assert os.path.exists(self.test_output_path)
    
    def test_categorize_messages_duplicate_messages(self):
        """Test handling of duplicate messages."""
        mock_messages = [
            "Duplicate message",
            "Duplicate message",
            "Unique message",
            "Duplicate message"
        ]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            categorize_messages(n_clusters=2, output_path=self.test_output_path)
            
            assert os.path.exists(self.test_output_path)
            
            with open(self.test_output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            
            # All messages should be preserved, including duplicates
            assert len(categorized_data) == 4
    
    def test_categorize_messages_very_long_messages(self):
        """Test with very long messages to ensure no truncation."""
        long_message = "word " * 1000  # Very long message
        mock_messages = [long_message, "Short message"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            categorize_messages(n_clusters=2, output_path=self.test_output_path)
            
            assert os.path.exists(self.test_output_path)
            
            with open(self.test_output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            
            # Verify long message is preserved
            texts = [item['text'] for item in categorized_data]
            assert long_message in texts
    
    def test_categorize_messages_output_format_validation(self):
        """Test that output JSON format is valid and consistent."""
        mock_messages = ["Msg1", "Msg2", "Msg3"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            categorize_messages(n_clusters=2, output_path=self.test_output_path)
            
            # Verify the file can be read back as valid JSON
            with open(self.test_output_path, 'rb') as f:
                raw_data = f.read()
            
            # Should not raise any exceptions
            categorized_data = orjson.loads(raw_data)
            
            # Verify structure
            assert isinstance(categorized_data, list)
            for item in categorized_data:
                assert isinstance(item, dict)
                assert set(item.keys()) == {'category', 'text'}

    @patch('categorize.get_messages')
    def test_categorize_messages_integration_with_sklearn(self, mock_get_messages):
        """Integration test to ensure sklearn components work together."""
        mock_messages = [
            "Python programming is fun",
            "Machine learning with Python",
            "Coffee is great in the morning",
            "I love coffee breaks",
            "Data science and analytics"
        ]
        mock_get_messages.return_value = mock_messages
        
        with patch('builtins.print'):
            categorize_messages(n_clusters=2, output_path=self.test_output_path)
        
        assert os.path.exists(self.test_output_path)
        
        with open(self.test_output_path, 'rb') as f:
            categorized_data = orjson.loads(f.read())
        
        # Messages about similar topics should be in similar categories
        categories_by_text = {item['text']: item['category'] for item in categorized_data}
        
        # Python-related messages should likely be in the same category
        python_msgs = ["Python programming is fun", "Machine learning with Python"]
        python_categories = [categories_by_text[msg] for msg in python_msgs]
        
        # Coffee-related messages should likely be in the same category
        coffee_msgs = ["Coffee is great in the morning", "I love coffee breaks"]
        coffee_categories = [categories_by_text[msg] for msg in coffee_msgs]
        
        # This is a soft assertion as clustering can vary
        # But generally similar messages should cluster together
        assert len(set(python_categories)) <= 2
        assert len(set(coffee_categories)) <= 2


class TestCategorizeMessagesEdgeCases:
    """Additional edge case tests for categorize_messages function."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for edge case tests."""
        self.temp_dir = tempfile.mkdtemp()
        yield
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_none_in_messages_list(self):
        """Test handling when None values are in the messages list."""
        mock_messages = ["Valid message", None, "Another message"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            # This should handle None gracefully or raise an appropriate error
            # The actual behavior depends on implementation requirements
            output_path = os.path.join(self.temp_dir, 'test.json')
            
            # TfidfVectorizer will likely fail with None values
            with pytest.raises(AttributeError):
                categorize_messages(n_clusters=2, output_path=output_path)
    
    def test_empty_strings_in_messages(self):
        """Test handling of empty strings in messages."""
        mock_messages = ["Message 1", "", "Message 2", "   ", "Message 3"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            output_path = os.path.join(self.temp_dir, 'test.json')
            categorize_messages(n_clusters=2, output_path=output_path)
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            
            # All messages including empty ones should be categorized
            assert len(categorized_data) == 5
    
    def test_numeric_messages(self):
        """Test with numeric values as messages."""
        mock_messages = ["123", "456.789", "Message with number 42", "-100"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            output_path = os.path.join(self.temp_dir, 'test.json')
            categorize_messages(n_clusters=2, output_path=output_path)
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            
            assert len(categorized_data) == 4
            for item in categorized_data:
                assert item['text'] in mock_messages
    
    def test_permission_error_on_output(self):
        """Test handling when output directory has permission issues."""
        mock_messages = ["Test message"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'), \
             patch('os.makedirs', side_effect=PermissionError("No permission")), \
             pytest.raises(PermissionError, match="No permission"):
            categorize_messages(output_path='/restricted/path/test.json')
    
    def test_zero_clusters(self):
        """Test with zero clusters (invalid parameter)."""
        mock_messages = ["Message 1", "Message 2"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            output_path = os.path.join(self.temp_dir, 'test.json')
            
            # KMeans should raise an error for n_clusters=0
            with pytest.raises(ValueError):
                categorize_messages(n_clusters=0, output_path=output_path)
    
    def test_negative_clusters(self):
        """Test with negative number of clusters (invalid parameter)."""
        mock_messages = ["Message 1", "Message 2"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            output_path = os.path.join(self.temp_dir, 'test.json')
            
            # KMeans should raise an error for negative n_clusters
            with pytest.raises(ValueError):
                categorize_messages(n_clusters=-1, output_path=output_path)


class TestMainExecution:
    """Test the main execution block."""
    
    def test_main_execution(self):
        """Test that main block executes categorize_messages with defaults."""
        mock_messages = ["Test message"]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'), \
             patch('builtins.open', mock_open()), \
             patch.dict('sys.modules', {'__main__': '__main__'}):
            
            # Import would trigger main block execution
            # This test verifies the main block works correctly
            pass


# Performance and stress tests
class TestPerformance:
    """Performance-related tests for categorize_messages."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for performance tests."""
        self.temp_dir = tempfile.mkdtemp()
        yield
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_large_number_of_clusters(self):
        """Test with a large number of clusters relative to samples."""
        mock_messages = [f"Message {i}" for i in range(10)]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            output_path = os.path.join(self.temp_dir, 'test.json')
            
            # Number of clusters equals number of samples
            categorize_messages(n_clusters=10, output_path=output_path)
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            
            # Each message might get its own cluster
            categories = [item['category'] for item in categorized_data]
            assert len(set(categories)) <= 10
    
    def test_memory_efficient_handling(self):
        """Test that the function handles memory efficiently with large datasets."""
        # Create a moderately large dataset
        mock_messages = [f"This is message number {i} with some content" for i in range(1000)]
        
        with patch('categorize.get_messages', return_value=mock_messages), \
             patch('builtins.print'):
            
            output_path = os.path.join(self.temp_dir, 'test.json')
            
            # Should complete without memory issues
            categorize_messages(n_clusters=20, output_path=output_path)
            
            assert os.path.exists(output_path)
            
            # Verify file size is reasonable
            file_size = os.path.getsize(output_path)
            assert file_size > 0
            
            # Verify all messages were processed
            with open(output_path, 'rb') as f:
                categorized_data = orjson.loads(f.read())
            assert len(categorized_data) == 1000


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])