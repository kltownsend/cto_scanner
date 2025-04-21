from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import os

class ReportGenerator:
    def __init__(self, output_path=None, max_reports=30):
        """
        Initialize the report generator.
        
        Args:
            output_path: Optional custom path for the PDF
            max_reports: Maximum number of reports to keep (default 30)
        """
        # Determine base directory
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        
        # Create reports directory structure
        self.reports_dir = self.base_dir / 'reports'
        self.reports_dir.mkdir(exist_ok=True)
        
        # Create dated subdirectory
        today = datetime.now().strftime("%Y-%m")
        self.current_month_dir = self.reports_dir / today
        self.current_month_dir.mkdir(exist_ok=True)
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.current_month_dir / f"tech_report_{timestamp}.pdf"
        
        self.doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='Link',
            parent=self.styles['Normal'],
            textColor=colors.blue,
            underline=True
        ))
        
        self.styles.add(ParagraphStyle(
            name='Rating',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkgreen
        ))
        
        # Clean up old reports
        self.cleanup_old_reports(max_reports)

    def cleanup_old_reports(self, max_reports):
        """Remove old reports keeping only the specified number of most recent ones."""
        # Get all PDF files from all subdirectories
        all_reports = []
        for month_dir in self.reports_dir.glob("*"):
            if month_dir.is_dir():
                all_reports.extend(month_dir.glob("*.pdf"))
        
        # Sort by creation time (newest first)
        all_reports.sort(key=lambda x: x.stat().st_ctime, reverse=True)
        
        # Remove excess reports
        if len(all_reports) > max_reports:
            for old_report in all_reports[max_reports:]:
                old_report.unlink()
            
            # Clean up empty directories
            for month_dir in self.reports_dir.glob("*"):
                if month_dir.is_dir() and not any(month_dir.iterdir()):
                    month_dir.rmdir()

    def add_header(self, days_back):
        """Add header to the report."""
        title = f"CTO Signal Scanner Report"
        date_range = f"Articles from the last {days_back} days"
        generated = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.story.append(Paragraph(title, self.styles['Heading1']))
        self.story.append(Paragraph(date_range, self.styles['Heading2']))
        self.story.append(Paragraph(generated, self.styles['Normal']))
        self.story.append(Spacer(1, 20))

    def add_article(self, article_data):
        """Add an article to the report.
        
        Args:
            article_data: Dictionary containing article data with keys:
                - title: Article title
                - link: Article URL
                - summary: Article summary
                - rating: Article rating
                - rationale: Article rationale
        """
        # Add title with link
        title_text = f'<link href="{article_data["link"]}">{article_data["title"]}</link>'
        self.story.append(Paragraph(title_text, self.styles['Link']))
        self.story.append(Spacer(1, 10))
        
        # Add rating
        rating_text = f'Rating: {article_data["rating"]}'
        self.story.append(Paragraph(rating_text, self.styles['Rating']))
        self.story.append(Spacer(1, 10))
        
        # Add summary
        self.story.append(Paragraph("Summary:", self.styles['Heading3']))
        self.story.append(Paragraph(article_data["summary"], self.styles['Normal']))
        self.story.append(Spacer(1, 10))
        
        # Add rationale
        self.story.append(Paragraph("Rationale:", self.styles['Heading3']))
        self.story.append(Paragraph(article_data["rationale"], self.styles['Normal']))
        self.story.append(Spacer(1, 20))

    def generate(self):
        """Generate the PDF report."""
        try:
            # Add a message if no articles were processed
            if not self.story:
                self.story.append(Paragraph("No articles were processed in this scan.", self.styles['Normal']))
                self.story.append(Spacer(1, 20))
                self.story.append(Paragraph("This could be due to:", self.styles['Normal']))
                self.story.append(Paragraph("1. No new articles found in the specified time range", self.styles['Normal']))
                self.story.append(Paragraph("2. Issues with feed sources", self.styles['Normal']))
                self.story.append(Paragraph("3. API authentication errors", self.styles['Normal']))
            
            # Build the PDF
            self.doc.build(self.story)
            
            # Return the path to the generated PDF
            return Path(self.doc.filename)
            
        except Exception as e:
            # Log the error
            import logging
            logging.error(f"Error generating PDF: {str(e)}")
            
            # Create a basic error report
            error_path = self.current_month_dir / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            error_doc = SimpleDocTemplate(
                str(error_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            error_story = []
            error_story.append(Paragraph("Error Generating Report", self.styles['Heading1']))
            error_story.append(Spacer(1, 20))
            error_story.append(Paragraph(f"An error occurred while generating the report: {str(e)}", self.styles['Normal']))
            error_story.append(Spacer(1, 20))
            error_story.append(Paragraph("Please check the application logs for more details.", self.styles['Normal']))
            
            error_doc.build(error_story)
            return error_path 