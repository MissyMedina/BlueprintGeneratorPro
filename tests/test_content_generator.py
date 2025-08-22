#!/usr/bin/env python3
"""
Unit tests for the Content Generator
"""

import unittest
import sys
import os

# Add the web_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web_app'))

from content_generator import ContentGenerator

class TestContentGenerator(unittest.TestCase):
    """Test cases for the ContentGenerator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = ContentGenerator()

    def test_generator_initialization(self):
        """Test that the generator initializes correctly"""
        self.assertIsInstance(self.generator, ContentGenerator)
        self.assertIsInstance(self.generator.project_types, dict)
        self.assertGreater(len(self.generator.project_types), 0)
    
    def test_prd_generation(self):
        """Test PRD document generation"""
        prd_content = self.generator.generate_prd_content(
            project_name='Test Project',
            project_type='web-app',
            description='A test project for unit testing',
            custom_answers={},
            focus_area='technical'
        )

        # Check that PRD contains expected sections
        self.assertIn('# Product Requirements Document', prd_content)
        self.assertIn('Test Project', prd_content)
        self.assertIn('A test project for unit testing', prd_content)
        self.assertIn('## Executive Summary', prd_content)
        self.assertIn('## Technical Requirements', prd_content)
    
    def test_readme_generation(self):
        """Test README document generation"""
        readme_content = self.generator.generate_readme_content(
            project_name='Test API',
            project_type='api',
            description='A REST API for testing',
            custom_answers={}
        )

        # Check that README contains expected sections
        self.assertIn('# Test API', readme_content)
        self.assertIn('A REST API for testing', readme_content)
        self.assertIn('## Installation', readme_content)
        self.assertIn('## Usage', readme_content)
        self.assertIn('## API Documentation', readme_content)
    
    def test_project_types(self):
        """Test that project types are properly defined"""
        self.assertIn('web-app', self.generator.project_types)
        self.assertIn('mobile-app', self.generator.project_types)
        self.assertIn('api', self.generator.project_types)

        # Test project type structure
        web_app = self.generator.project_types['web-app']
        self.assertIn('description', web_app)
        self.assertIn('common_features', web_app)
        self.assertIn('tech_considerations', web_app)
        self.assertIn('security_focus', web_app)
    
    def test_different_project_types(self):
        """Test content generation for different project types"""
        # Test web app
        web_readme = self.generator.generate_readme_content(
            project_name='Web App',
            project_type='web-app',
            description='A web application',
            custom_answers={}
        )
        self.assertIn('Web App', web_readme)
        self.assertIn('web application', web_readme.lower())

        # Test API
        api_readme = self.generator.generate_readme_content(
            project_name='API Service',
            project_type='api',
            description='A REST API service',
            custom_answers={}
        )
        self.assertIn('API Service', api_readme)
        self.assertIn('api', api_readme.lower())
    
    def test_focus_area_impact(self):
        """Test that focus area affects content generation"""
        base_data = {
            'project': 'Test Project',
            'description': 'A test project',
            'components': ['frontend', 'backend'],
            'docType': 'prd',
            'customAnswers': {}
        }
        
        # Test technical focus
        technical_data = {**base_data, 'focusArea': 'technical'}
        technical_prd = self.generator.generate_prd(technical_data)
        
        # Test business focus
        business_data = {**base_data, 'focusArea': 'business'}
        business_prd = self.generator.generate_prd(business_data)
        
        # Content should be different based on focus
        self.assertNotEqual(technical_prd, business_prd)
    
    def test_custom_answers_integration(self):
        """Test that custom answers are integrated into content"""
        project_data = {
            'project': 'Custom Project',
            'description': 'Project with custom answers',
            'components': ['frontend'],
            'docType': 'prd',
            'focusArea': 'technical',
            'customAnswers': {
                'target_audience': 'Developers and technical users',
                'key_features': 'Real-time updates, API integration',
                'success_metrics': 'User engagement, performance metrics'
            }
        }
        
        prd_content = self.generator.generate_prd(project_data)
        
        # Check that custom answers are included
        self.assertIn('Developers and technical users', prd_content)
        self.assertIn('Real-time updates', prd_content)
        self.assertIn('User engagement', prd_content)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with missing required fields
        invalid_data = {
            'project': '',  # Empty project name
            'description': 'Test description',
            'components': [],  # No components
            'docType': 'prd',
            'focusArea': 'technical',
            'customAnswers': {}
        }
        
        # Should still generate content without crashing
        try:
            content = self.generator.generate_prd(invalid_data)
            self.assertIsInstance(content, str)
            self.assertGreater(len(content), 0)
        except Exception as e:
            self.fail(f"Generator should handle invalid data gracefully: {e}")
    
    def test_content_quality(self):
        """Test that generated content meets quality standards"""
        project_data = {
            'project': 'Quality Test Project',
            'description': 'Testing content quality standards',
            'components': ['frontend', 'backend', 'database'],
            'docType': 'prd',
            'focusArea': 'technical',
            'customAnswers': {}
        }
        
        content = self.generator.generate_prd(project_data)
        
        # Check content quality metrics
        self.assertGreater(len(content), 1000)  # Should be substantial
        self.assertIn('#', content)  # Should have headers
        self.assertIn('##', content)  # Should have subheaders
        self.assertGreater(content.count('\n'), 20)  # Should have multiple lines
        
        # Check for professional language
        professional_terms = ['requirements', 'objectives', 'implementation', 'technical']
        self.assertTrue(any(term in content.lower() for term in professional_terms))

class TestContentGeneratorIntegration(unittest.TestCase):
    """Integration tests for content generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = ContentGenerator()
    
    def test_all_document_types(self):
        """Test generation of all document types"""
        project_data = {
            'project': 'Integration Test Project',
            'description': 'Testing all document types',
            'components': ['frontend', 'backend', 'database'],
            'focusArea': 'technical',
            'customAnswers': {}
        }
        
        # Test all document types
        doc_types = ['prd', 'readme', 'mvp', 'security']
        
        for doc_type in doc_types:
            with self.subTest(doc_type=doc_type):
                test_data = {**project_data, 'docType': doc_type}
                
                if doc_type == 'prd':
                    content = self.generator.generate_prd(test_data)
                elif doc_type == 'readme':
                    content = self.generator.generate_readme(test_data)
                elif doc_type == 'mvp':
                    content = self.generator.generate_mvp(test_data)
                elif doc_type == 'security':
                    content = self.generator.generate_security_audit(test_data)
                
                # Verify content was generated
                self.assertIsInstance(content, str)
                self.assertGreater(len(content), 100)
                self.assertIn('Integration Test Project', content)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
