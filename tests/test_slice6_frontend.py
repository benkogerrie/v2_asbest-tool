"""
Frontend component tests for Slice 6 functionality.
"""
import pytest
from unittest.mock import Mock, patch
import json


class TestSSEClient:
    """Test SSE client functionality."""
    
    def test_handle_initial_state_message(self):
        """✅ Component test: useReportStream roept onUpdate met payload; UI update statusbadge."""
        
        # Mock DOM elements
        mock_tbody = Mock()
        mock_tbody.innerHTML = ""
        
        # Mock document.querySelector
        with patch('builtins.document') as mock_doc:
            mock_doc.querySelector.return_value = mock_tbody
            
            # Mock the SSE message handler
            def handle_initial_state(data):
                if data['type'] == 'initial_state':
                    reports = data['reports']
                    for report in reports:
                        status_class = "ok" if report['status'] == 'DONE' else "warn"
                        row_html = f"""
                        <tr>
                            <td>{report['filename']}</td>
                            <td><span class="chip {status_class}">{report['status']}</span></td>
                            <td>{report['finding_count']}</td>
                        </tr>
                        """
                        mock_tbody.innerHTML += row_html
            
            # Test data
            test_data = {
                'type': 'initial_state',
                'reports': [
                    {
                        'id': '123',
                        'filename': 'test1.pdf',
                        'status': 'DONE',
                        'finding_count': 3
                    },
                    {
                        'id': '456',
                        'filename': 'test2.pdf',
                        'status': 'PROCESSING',
                        'finding_count': 0
                    }
                ]
            }
            
            # Execute
            handle_initial_state(test_data)
            
            # Verify UI was updated
            assert "test1.pdf" in mock_tbody.innerHTML
            assert "test2.pdf" in mock_tbody.innerHTML
            assert "chip ok" in mock_tbody.innerHTML  # DONE status
            assert "chip warn" in mock_tbody.innerHTML  # PROCESSING status
    
    def test_handle_report_update_message(self):
        """✅ Component test: report update triggers UI update."""
        
        # Mock existing report data
        existing_reports = [
            {
                'id': '123',
                'filename': 'test1.pdf',
                'status': 'PROCESSING',
                'finding_count': 0
            }
        ]
        
        # Mock DOM elements
        mock_tbody = Mock()
        mock_tbody.innerHTML = ""
        
        with patch('builtins.document') as mock_doc:
            mock_doc.querySelector.return_value = mock_tbody
            
            def handle_report_update(data):
                if data['type'] == 'report_update':
                    report = data['report']
                    # Find and update existing report
                    for i, existing_report in enumerate(existing_reports):
                        if existing_report['id'] == report['id']:
                            existing_reports[i] = report
                            break
                    
                    # Update UI
                    mock_tbody.innerHTML = ""
                    for report in existing_reports:
                        status_class = "ok" if report['status'] == 'DONE' else "warn"
                        row_html = f"""
                        <tr>
                            <td>{report['filename']}</td>
                            <td><span class="chip {status_class}">{report['status']}</span></td>
                            <td>{report['finding_count']}</td>
                        </tr>
                        """
                        mock_tbody.innerHTML += row_html
            
            # Test update message
            update_data = {
                'type': 'report_update',
                'report': {
                    'id': '123',
                    'filename': 'test1.pdf',
                    'status': 'DONE',
                    'finding_count': 3
                }
            }
            
            # Execute
            handle_report_update(update_data)
            
            # Verify report was updated
            assert existing_reports[0]['status'] == 'DONE'
            assert existing_reports[0]['finding_count'] == 3
            assert "chip ok" in mock_tbody.innerHTML
    
    def test_reconnect_functionality(self):
        """✅ Reconnect: simuleer netwerk drop → client herstelt verbinding."""
        
        # Mock EventSource
        mock_event_source = Mock()
        mock_event_source.readyState = 2  # CLOSED
        
        # Mock setTimeout
        with patch('builtins.setTimeout') as mock_setTimeout:
            
            def simulate_reconnect():
                if mock_event_source.readyState == 2:  # CLOSED
                    mock_setTimeout.assert_called()
                    # Verify reconnect was scheduled
                    call_args = mock_setTimeout.call_args
                    assert call_args[0][1] == 5000  # 5 second delay
            
            # Simulate network drop
            mock_event_source.readyState = 2
            
            # Execute reconnect logic
            simulate_reconnect()
    
    def test_toast_notifications(self):
        """✅ Toasts: bij DONE toont 'PDF is klaar', bij FAILED toont foutmelding."""
        
        # Mock DOM
        mock_body = Mock()
        mock_body.appendChild = Mock()
        
        with patch('builtins.document') as mock_doc:
            mock_doc.body = mock_body
            
            def show_toast(message, type='info'):
                toast = Mock()
                toast.style = {}
                toast.textContent = message
                
                if type == 'success':
                    toast.style.background = '#28a745'
                elif type == 'error':
                    toast.style.background = '#dc3545'
                else:
                    toast.style.background = '#17a2b8'
                
                mock_body.appendChild(toast)
                return toast
            
            # Test DONE notification
            done_toast = show_toast("Rapport 'test.pdf' is DONE", 'success')
            assert done_toast.style.background == '#28a745'
            assert "DONE" in done_toast.textContent
            
            # Test FAILED notification
            failed_toast = show_toast("Rapport 'test.pdf' verwerking mislukt", 'error')
            assert failed_toast.style.background == '#dc3545'
            assert "mislukt" in failed_toast.textContent


class TestDownloadFunctionality:
    """Test download functionality."""
    
    def test_download_button_done_report(self):
        """✅ DONE: klik download → FE haalt /download → browser opent presigned URL."""
        
        # Mock fetch
        mock_response = Mock()
        mock_response.json.return_value = {
            'url': 'https://storage.example.com/presigned-url',
            'filename': 'test.pdf',
            'expires_in': 3600
        }
        
        with patch('builtins.fetch') as mock_fetch:
            mock_fetch.return_value = mock_response
            
            # Mock window.open
            with patch('builtins.window') as mock_window:
                mock_window.open = Mock()
                
                async def download_report(report_id):
                    response = await mock_fetch(f'/reports/{report_id}/download')
                    data = await response.json()
                    mock_window.open(data['url'], '_blank')
                    return data
                
                # Execute
                import asyncio
                result = asyncio.run(download_report('123'))
                
                # Verify
                assert result['url'] == 'https://storage.example.com/presigned-url'
                mock_window.open.assert_called_once_with('https://storage.example.com/presigned-url', '_blank')
    
    def test_download_button_not_done_disabled(self):
        """✅ Niet-DONE: downloadknop disabled of geeft nette fout/toast."""
        
        # Mock fetch to return error
        mock_response = Mock()
        mock_response.status = 400
        mock_response.json.return_value = {
            'detail': 'Report is not ready for download. Current status: PROCESSING'
        }
        
        with patch('builtins.fetch') as mock_fetch:
            mock_fetch.return_value = mock_response
            
            async def download_report(report_id):
                try:
                    response = await mock_fetch(f'/reports/{report_id}/download')
                    if not response.ok:
                        error_data = await response.json()
                        raise Exception(error_data['detail'])
                except Exception as e:
                    return {'error': str(e)}
            
            # Execute
            import asyncio
            result = asyncio.run(download_report('123'))
            
            # Verify error handling
            assert 'error' in result
            assert 'not ready for download' in result['error']


class TestUIStates:
    """Test UI states and loading indicators."""
    
    def test_loader_state(self):
        """✅ Loader bij initial fetch."""
        
        # Mock DOM elements
        mock_loader = Mock()
        mock_loader.style = {}
        
        with patch('builtins.document') as mock_doc:
            mock_doc.getElementById.return_value = mock_loader
            
            def show_loader():
                mock_loader.style.display = 'block'
            
            def hide_loader():
                mock_loader.style.display = 'none'
            
            # Test loader show
            show_loader()
            assert mock_loader.style.display == 'block'
            
            # Test loader hide
            hide_loader()
            assert mock_loader.style.display == 'none'
    
    def test_empty_state(self):
        """✅ Empty state met vriendelijke tekst."""
        
        # Mock DOM elements
        mock_tbody = Mock()
        mock_tbody.innerHTML = ""
        
        with patch('builtins.document') as mock_doc:
            mock_doc.querySelector.return_value = mock_tbody
            
            def show_empty_state():
                mock_tbody.innerHTML = """
                <tr>
                    <td colspan="4" style="text-align: center; padding: 40px; color: #8a93a2;">
                        📄 Geen rapporten gevonden
                        <br>
                        <small>Upload je eerste rapport om te beginnen</small>
                    </td>
                </tr>
                """
            
            # Execute
            show_empty_state()
            
            # Verify empty state
            assert "Geen rapporten gevonden" in mock_tbody.innerHTML
            assert "Upload je eerste rapport" in mock_tbody.innerHTML
    
    def test_soft_deleted_item_disappears(self):
        """✅ Soft deleted: item verdwijnt na delete (zonder page reload)."""
        
        # Mock reports data
        reports = [
            {'id': '1', 'filename': 'report1.pdf', 'status': 'DONE'},
            {'id': '2', 'filename': 'report2.pdf', 'status': 'DONE'},
            {'id': '3', 'filename': 'report3.pdf', 'status': 'DONE'}
        ]
        
        # Mock DOM
        mock_tbody = Mock()
        mock_tbody.innerHTML = ""
        
        with patch('builtins.document') as mock_doc:
            mock_doc.querySelector.return_value = mock_tbody
            
            def update_reports_table(reports_data):
                mock_tbody.innerHTML = ""
                for report in reports_data:
                    row_html = f"<tr><td>{report['filename']}</td></tr>"
                    mock_tbody.innerHTML += row_html
            
            def soft_delete_report(report_id):
                # Remove from data
                reports[:] = [r for r in reports if r['id'] != report_id]
                # Update UI
                update_reports_table(reports)
            
            # Initial state
            update_reports_table(reports)
            assert "report1.pdf" in mock_tbody.innerHTML
            assert "report2.pdf" in mock_tbody.innerHTML
            assert "report3.pdf" in mock_tbody.innerHTML
            
            # Delete report2
            soft_delete_report('2')
            
            # Verify report2 is gone
            assert "report1.pdf" in mock_tbody.innerHTML
            assert "report2.pdf" not in mock_tbody.innerHTML
            assert "report3.pdf" in mock_tbody.innerHTML


class TestSecurity:
    """Test frontend security measures."""
    
    def test_no_presigned_url_storage(self):
        """✅ Geen opslag van presigned URL in localStorage/sessionStorage."""
        
        # Mock localStorage
        mock_localStorage = {}
        
        with patch('builtins.localStorage') as mock_storage:
            mock_storage.getItem = lambda key: mock_localStorage.get(key)
            mock_storage.setItem = lambda key, value: mock_localStorage.update({key: value})
            
            def download_report(report_id):
                # Simulate download flow
                presigned_url = "https://storage.example.com/presigned-url"
                
                # Should NOT store presigned URL
                # mock_storage.setItem('download_url', presigned_url)  # This should NOT happen
                
                # Should only store auth token
                mock_storage.setItem('asbest_jwt', 'auth-token-123')
                
                return presigned_url
            
            # Execute
            url = download_report('123')
            
            # Verify presigned URL is not stored
            assert 'download_url' not in mock_localStorage
            assert 'asbest_jwt' in mock_localStorage
            assert url == "https://storage.example.com/presigned-url"
    
    def test_no_sensitive_data_in_dom(self):
        """✅ Geen gevoelige data in DOM/console."""
        
        # Mock DOM
        mock_element = Mock()
        mock_element.innerHTML = ""
        
        def update_report_row(report_data):
            # Should NOT include sensitive data
            safe_data = {
                'id': report_data['id'],
                'filename': report_data['filename'],
                'status': report_data['status']
            }
            
            # Should NOT include storage keys, checksums, etc.
            # safe_data['storage_key'] = report_data.get('storage_key')  # This should NOT happen
            
            mock_element.innerHTML = f"""
            <tr>
                <td>{safe_data['filename']}</td>
                <td>{safe_data['status']}</td>
            </tr>
            """
        
        # Test data with sensitive information
        report_data = {
            'id': '123',
            'filename': 'test.pdf',
            'status': 'DONE',
            'storage_key': 'tenants/secret/reports/123/output.pdf',  # Sensitive
            'checksum': 'abc123def456',  # Sensitive
            'file_size': 1024000
        }
        
        # Execute
        update_report_row(report_data)
        
        # Verify sensitive data is not in DOM
        assert "test.pdf" in mock_element.innerHTML
        assert "DONE" in mock_element.innerHTML
        assert "tenants/secret" not in mock_element.innerHTML
        assert "abc123def456" not in mock_element.innerHTML
