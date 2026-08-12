"""
PDF Exporter for ESS RAG Chatbot Conversations
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor
from datetime import datetime
import os


class PDFExporter:
    """Export conversations to PDF format"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        # Use absolute path to ensure logo is found regardless of working directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.logo_path = os.path.join(base_dir, "assets", "ess_logo_fixed.png")
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            fontName='Times-Bold',  # Times New Roman Bold
            textColor=HexColor('#4ade80'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Times-Roman',  # Times New Roman
            textColor=HexColor('#6B9BD1'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Question style
        self.styles.add(ParagraphStyle(
            name='Question',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Times-Bold',  # Times New Roman Bold
            textColor=HexColor('#4ade80'),
            spaceAfter=8,
            leftIndent=0
        ))
        
        # Answer style
        self.styles.add(ParagraphStyle(
            name='Answer',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Times-Roman',  # Times New Roman
            textColor=HexColor('#e0e0e0'),
            spaceAfter=8,
            leftIndent=10,
            leading=14
        ))
        
        # Metadata style
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Times-Italic',  # Times New Roman Italic
            textColor=HexColor('#94a3b8'),
            spaceAfter=20,
            leftIndent=10
        ))
    
    def export_conversation(self, messages, filename=None):
        """
        Export conversation to PDF
        
        Args:
            messages: List of message dictionaries with 'role', 'content', 'metadata'
            filename: Output filename (optional, auto-generated if not provided)
            
        Returns:
            dict: {'success': bool, 'filename': str, 'error': str}
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"ess_conversation_{timestamp}.pdf"
            
            # Ensure output directory exists
            output_dir = "exports"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build content
            story = []
            
            # Add ESS logo at the top
            if os.path.exists(self.logo_path):
                try:
                    logo = Image(self.logo_path, width=1.5*inch, height=1.5*inch)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 0.2*inch))
                except Exception as logo_err:
                    # Log error but continue without logo
                    print(f"Warning: Could not add logo to PDF: {logo_err}")
            else:
                print(f"Warning: Logo file not found at: {self.logo_path}")
            
            # Add header
            story.append(Paragraph("Ethiopian Statistics Service", self.styles['CustomTitle']))
            story.append(Paragraph("RAG Chatbot Conversation Export", self.styles['CustomSubtitle']))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 0.3*inch))
            
            # Add Q&A pairs
            for idx, msg in enumerate(messages, 1):
                if msg['role'] == 'user':
                    # Question
                    question_text = f"<b>Q{idx}:</b> {self._escape_html(msg['content'])}"
                    story.append(Paragraph(question_text, self.styles['Question']))
                    
                elif msg['role'] == 'assistant':
                    # Answer
                    answer_text = f"<b>A:</b> {self._escape_html(msg['content'])}"
                    story.append(Paragraph(answer_text, self.styles['Answer']))
                    
                    # Metadata
                    if 'metadata' in msg:
                        metadata = msg['metadata']
                        meta_text = f"<i>Response Time: {metadata.get('time', 0):.2f}s | "
                        meta_text += f"Engines: {', '.join(metadata.get('engines', []))} | "
                        meta_text += f"Sources: {metadata.get('sources', 0)}</i>"
                        story.append(Paragraph(meta_text, self.styles['Metadata']))
                    
                    # Add separator
                    story.append(Spacer(1, 0.2*inch))
            
            # Add footer
            story.append(Spacer(1, 0.5*inch))
            footer_text = "<i>This document contains AI-generated responses based on Ethiopian Statistics Service data and reports.</i>"
            story.append(Paragraph(footer_text, self.styles['Metadata']))
            
            # Build PDF
            doc.build(story)
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'filename': None,
                'filepath': None,
                'error': str(e)
            }
    
    def _escape_html(self, text):
        """Escape special HTML characters"""
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('\n', '<br/>')
        return text
