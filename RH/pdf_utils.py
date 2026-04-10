from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


def gerar_pdf_advertencia(advertencia):
    """
    Gera um PDF profissional da advertência para assinatura.
    Retorna um BytesIO com o conteúdo do PDF.
    """
    
    # Cria buffer em memória
    buffer = BytesIO()
    
    # Define documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#003366'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        fontName='Helvetica'
    )
    
    # Conteúdo do documento
    elements = []
    
    # Header
    elements.append(Paragraph("CAFÉ DO SÍTIO", titulo_style))
    elements.append(Paragraph("INDÚSTRIA E COMÉRCIO LTDA", heading_style))
    elements.append(Spacer(1, 12))
    
    # Título principal
    elements.append(Paragraph("TERMO DE ADVERTÊNCIA", titulo_style))
    elements.append(Spacer(1, 12))
    
    # Informações da advertência
    data_criacao = advertencia.CreatedAt.strftime("%d de %B de %Y").replace(
        'January', 'janeiro'
    ).replace('February', 'fevereiro').replace('March', 'março').replace(
        'April', 'abril'
    ).replace('May', 'maio').replace('June', 'junho').replace(
        'July', 'julho'
    ).replace('August', 'agosto').replace('September', 'setembro').replace(
        'October', 'outubro'
    ).replace('November', 'novembro').replace('December', 'dezembro')
    
    info_data = [
        ['IDENTIFICAÇÃO DO PROCESSO', f'Nº {advertencia.WarningID}'],
        ['DATA DE EMISSÃO', data_criacao],
        ['COLABORADOR', advertencia.ColaboradorID.Name],
        ['DEPARTAMENTO', advertencia.ColaboradorID.Department],
        ['CARGO', advertencia.ColaboradorID.Position],
        ['DATA DO OCORRIDO', advertencia.IncidentDate.strftime('%d/%m/%Y')],
    ]
    
    info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 16))
    
    # Descrição do ocorrido
    elements.append(Paragraph("DESCRIÇÃO DO OCORRIDO", heading_style))
    elements.append(Paragraph(advertencia.Description, normal_style))
    elements.append(Spacer(1, 12))
    
    # Texto oficial
    if advertencia.OfficialText:
        elements.append(Paragraph("TERMO DE ADVERTÊNCIA FORMAL", heading_style))
        elements.append(Paragraph(advertencia.OfficialText, normal_style))
    else:
        elements.append(Paragraph("TERMO DE ADVERTÊNCIA FORMAL", heading_style))
        elements.append(Paragraph(
            "Por este termo, fica registrada a advertência formal ao colaborador acima identificado, "
            "conforme descrito no item anterior, em conformidade com a legislação trabalhista vigente.",
            normal_style
        ))
    
    elements.append(Spacer(1, 20))
    
    # Data agendada
    if advertencia.SchenduledDate:
        data_agendada = advertencia.SchenduledDate.strftime('%d/%m/%Y')
        elements.append(Paragraph(f"<b>Data Prevista de Aplicação:</b> {data_agendada}", normal_style))
        elements.append(Spacer(1, 12))
    
    elements.append(Spacer(1, 20))
    
    # Assinaturas
    elements.append(Paragraph("ASSINATURAS E CIÊNCIA", heading_style))
    elements.append(Spacer(1, 16))
    
    assinatura_data = [
        ['', '', ''],
        ['_' * 40, '_' * 40, '_' * 40],
        ['Responsável TI', 'RH', 'Colaborador'],
        ['', '', ''],
        ['Data: _______________', 'Data: _______________', 'Data: _______________'],
    ]
    
    assinatura_table = Table(assinatura_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch])
    assinatura_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(assinatura_table)
    
    # Footer
    elements.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Documento gerado eletronicamente pelo Sistema de Gestão de Advertências", footer_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Retorna ao início do buffer
    buffer.seek(0)
    return buffer
