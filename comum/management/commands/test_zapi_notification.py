"""
Command para testar envio de mensagens Z-API
Uso: python manage.py test_zapi_notification
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from projeto_cafe.whatsapp_service import get_zapi_service
from TI.models import GestorTI
from RH.models import GestorRH
from Diretoria.models import GestorDiretoria


class Command(BaseCommand):
    help = 'Testa conexão e envio de mensagens via Z-API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            help='Número de telefone para teste (ex: 5511987654321)',
        )
        parser.add_argument(
            '--all-gestores',
            action='store_true',
            help='Enviar teste para todos os gestores cadastrados',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('🧪 TESTE Z-API NOTIFICATION'))
        self.stdout.write(self.style.WARNING('=' * 60))

        # Verificar configuração
        self._check_config()

        # Opção 1: Teste com número específico
        if options['phone']:
            self._test_phone(options['phone'])

        # Opção 2: Teste com todos os gestores
        elif options['all_gestores']:
            self._test_all_gestores()

        # Opção 3: Menu interativo
        else:
            self._interactive_menu()

        self.stdout.write(self.style.WARNING('=' * 60))

    def _check_config(self):
        """Verifica se as credenciais estão configuradas"""
        self.stdout.write('\n📋 Verificando Configuração...\n')

        instance_id = settings.ZAPI_INSTANCE_ID
        client_token = settings.ZAPI_CLIENT_TOKEN

        if not instance_id:
            raise CommandError(
                '❌ ZAPI_INSTANCE_ID não configurado! Adicione a .env'
            )
        
        if not client_token:
            raise CommandError(
                '❌ ZAPI_CLIENT_TOKEN não configurado! Adicione a .env'
            )

        self.stdout.write(
            self.style.SUCCESS(f'✅ Instance ID: {instance_id[:10]}...')
        )
        self.stdout.write(
            self.style.SUCCESS(f'✅ Client Token: {client_token[:10]}...')
        )

    def _test_phone(self, phone):
        """Testa envio para um número específico"""
        self.stdout.write(f'\n📱 Testando envio para: {phone}\n')

        servico = get_zapi_service()
        mensagem = (
            "🧪 *TESTE DO SISTEMA*\n\n"
            "Esta é uma mensagem de teste do Sistema de Gestão de Advertências.\n\n"
            f"Teste enviado: {self._get_timestamp()}"
        )

        resultado = servico.send_message(phone, mensagem)

        if resultado:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Mensagem enviada com sucesso para {phone}!'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Falha ao enviar para {phone}. Verifique:'
                    f'\n   - Número está correto? (ex: 5511987654321)'
                    f'\n   - Credenciais Z-API estão válidas?'
                    f'\n   - Z-API está ativo?'
                )
            )

    def _test_all_gestores(self):
        """Testa envio para todos os gestores cadastrados"""
        self.stdout.write('\n👥 Testando envio para todos os gestores\n')

        gestores_ti = GestorTI.objects.filter(Active=True)
        gestores_rh = GestorRH.objects.filter(Active=True)
        gestores_dir = GestorDiretoria.objects.filter(Active=True)

        self.stdout.write(f'   TI: {len(gestores_ti)} ativo(s)')
        self.stdout.write(f'   RH: {len(gestores_rh)} ativo(s)')
        self.stdout.write(f'   Diretoria: {len(gestores_dir)} ativo(s)')

        servico = get_zapi_service()

        for gestor in gestores_ti:
            if gestor.PhoneNumber:
                mensagem = f"📋 Teste para TI: {gestor.Name}"
                resultado = servico.send_message(gestor.PhoneNumber, mensagem)
                status = "✅" if resultado else "❌"
                self.stdout.write(f'{status} TI - {gestor.Name}: {gestor.PhoneNumber}')

        for gestor in gestores_rh:
            if gestor.PhoneNumber:
                mensagem = f"📋 Teste para RH: {gestor.Name}"
                resultado = servico.send_message(gestor.PhoneNumber, mensagem)
                status = "✅" if resultado else "❌"
                self.stdout.write(f'{status} RH - {gestor.Name}: {gestor.PhoneNumber}')

        for gestor in gestores_dir:
            if gestor.PhoneNumber:
                mensagem = f"📋 Teste para Diretoria: {gestor.Name}"
                resultado = servico.send_message(gestor.PhoneNumber, mensagem)
                status = "✅" if resultado else "❌"
                self.stdout.write(f'{status} DIR - {gestor.Name}: {gestor.PhoneNumber}')

    def _interactive_menu(self):
        """Menu interativo para escolher tipo de teste"""
        self.stdout.write('\n🔍 Escolha o tipo de teste:\n')
        self.stdout.write('1️⃣  Teste com número específico')
        self.stdout.write('2️⃣  Teste com todos os gestores')
        self.stdout.write('3️⃣  Informações de gestores cadastrados')

        opcao = input('\nDigite a opção (1-3): ').strip()

        if opcao == '1':
            phone = input('Digite o número (ex: 5511987654321): ').strip()
            self._test_phone(phone)

        elif opcao == '2':
            self._test_all_gestores()

        elif opcao == '3':
            self._show_gestores_info()

        else:
            self.stdout.write(self.style.ERROR('❌ Opção inválida!'))

    def _show_gestores_info(self):
        """Mostra informações de todos os gestores"""
        self.stdout.write('\n📞 INFORMAÇÕES DE GESTORES\n')

        self.stdout.write(self.style.WARNING('\n=== GESTORES TI ==='))
        for g in GestorTI.objects.all():
            ativo = "✅" if g.Active else "❌"
            phone = g.PhoneNumber or "Sem número"
            self.stdout.write(f'{ativo} {g.Name} - {phone}')

        self.stdout.write(self.style.WARNING('\n=== GESTORES RH ==='))
        for g in GestorRH.objects.all():
            ativo = "✅" if g.Active else "❌"
            phone = g.PhoneNumber or "Sem número"
            self.stdout.write(f'{ativo} {g.Name} - {phone}')

        self.stdout.write(self.style.WARNING('\n=== GESTORES DIRETORIA ==='))
        for g in GestorDiretoria.objects.all():
            ativo = "✅" if g.Active else "❌"
            phone = g.PhoneNumber or "Sem número"
            self.stdout.write(f'{ativo} {g.Name} - {phone}')

    def _get_timestamp(self):
        """Retorna timestamp formatado"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
