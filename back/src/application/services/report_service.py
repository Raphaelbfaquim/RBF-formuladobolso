from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO
import pandas as pd
import pytz
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from src.domain.repositories.transaction_repository import TransactionRepository
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.goal_repository import GoalRepository
from src.domain.repositories.planning_repository import PlanningRepository
from src.domain.repositories.bill_repository import BillRepository
from collections import defaultdict


class ReportService:
    """Serviço para geração de relatórios"""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
        goal_repository: GoalRepository,
        planning_repository: PlanningRepository,
        bill_repository: Optional[BillRepository] = None,
    ):
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository
        self.goal_repository = goal_repository
        self.planning_repository = planning_repository
        self.bill_repository = bill_repository

    async def generate_monthly_report_pdf(
        self, user_id: UUID, year: int, month: int
    ) -> BytesIO:
        """Gera relatório mensal em PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Título
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        story.append(Paragraph(f"Relatório Mensal - {month:02d}/{year}", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Período
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)

        # Obter dados
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        accounts = await self.account_repository.get_by_user_id(user_id)

        # Resumo Financeiro
        story.append(Paragraph("Resumo Financeiro", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))

        total_income = sum(
            float(t.amount) for t in transactions if t.transaction_type.value == "income"
        )
        total_expense = sum(
            float(t.amount) for t in transactions if t.transaction_type.value == "expense"
        )
        balance = total_income - total_expense

        summary_data = [
            ["Receitas", f"R$ {total_income:,.2f}"],
            ["Despesas", f"R$ {total_expense:,.2f}"],
            ["Saldo", f"R$ {balance:,.2f}"],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Transações
        story.append(Paragraph("Transações", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))

        if transactions:
            trans_data = [["Data", "Descrição", "Tipo", "Valor", "Categoria"]]
            for t in transactions[:50]:  # Limitar a 50 para não ficar muito longo
                trans_data.append(
                    [
                        t.transaction_date.strftime("%d/%m/%Y"),
                        t.description[:30],
                        t.transaction_type.value,
                        f"R$ {float(t.amount):,.2f}",
                        t.category.name if t.category else "-",
                    ]
                )

            trans_table = Table(trans_data, colWidths=[1 * inch, 2.5 * inch, 1 * inch, 1 * inch, 1.5 * inch])
            trans_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            story.append(trans_table)
        else:
            story.append(Paragraph("Nenhuma transação neste período.", styles["Normal"]))

        # Rodapé
        story.append(Spacer(1, 0.3 * inch))
        story.append(
            Paragraph(
                f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} - FormuladoBolso",
                styles["Normal"],
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer

    async def generate_transactions_excel(
        self, user_id: UUID, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> BytesIO:
        """Gera relatório de transações em Excel"""
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )

        data = []
        for t in transactions:
            data.append(
                {
                    "Data": t.transaction_date.strftime("%d/%m/%Y %H:%M"),
                    "Descrição": t.description,
                    "Tipo": t.transaction_type.value,
                    "Valor": float(t.amount),
                    "Status": t.status.value,
                    "Categoria": t.category.name if t.category else "",
                    "Conta": t.account.name if t.account else "",
                }
            )

        df = pd.DataFrame(data)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Transações")
        buffer.seek(0)
        return buffer

    async def generate_summary_data_for_family(
        self, family_id: UUID, start_date: datetime, end_date: datetime, db_session=None
    ) -> Dict:
        """Gera dados resumidos para dashboard de uma família"""
        if not db_session:
            print(f"⚠️ db_session não fornecido para generate_summary_data_for_family")
            return {
                "total_balance": 0,
                "monthly_income": 0,
                "monthly_expenses": 0,
                "monthly_savings": 0,
                "recent_transactions": [],
            }
        
        # Buscar todas as contas da família (com family_id) usando SQL direto
        from sqlalchemy import text
        account_ids = []
        try:
            account_ids_result = await db_session.execute(
                text("""
                    SELECT id FROM accounts 
                    WHERE family_id = :family_id AND is_active = true
                """),
                {"family_id": str(family_id)}
            )
            account_ids = [row[0] for row in account_ids_result.fetchall()]
            print(f"📊 Contas com family_id={family_id}: {len(account_ids)}")
        except Exception as e:
            print(f"⚠️ Erro ao buscar contas com family_id: {e}")
            account_ids = []
        
        # Buscar contas de todos os membros da família
        try:
            # Buscar user_ids dos membros usando SQL direto (evita greenlet error)
            result = await db_session.execute(
                text("SELECT user_id FROM family_members WHERE family_id = :family_id"),
                {"family_id": str(family_id)}
            )
            member_user_ids = [row[0] for row in result.fetchall()]
            print(f"📊 Membros da família {family_id}: {len(member_user_ids)} user_ids encontrados")
            
            # Buscar IDs de contas de cada membro usando SQL direto
            for member_user_id in member_user_ids:
                try:
                    member_accounts_result = await db_session.execute(
                        text("SELECT id FROM accounts WHERE owner_id = :user_id AND is_active = true"),
                        {"user_id": str(member_user_id)}
                    )
                    member_account_ids = [row[0] for row in member_accounts_result.fetchall()]
                    print(f"📊 Contas do membro {member_user_id}: {len(member_account_ids)}")
                    # Adicionar IDs que ainda não estão na lista
                    for acc_id in member_account_ids:
                        if acc_id not in account_ids:
                            account_ids.append(acc_id)
                except Exception as e:
                    print(f"⚠️ Erro ao buscar contas do membro {member_user_id}: {e}")
                    continue
            
            print(f"📊 Total de IDs de contas após buscar membros: {len(account_ids)}")
        except Exception as e:
            print(f"⚠️ Erro ao buscar membros da família: {e}")
            import traceback
            traceback.print_exc()
        
        # Buscar transações de todas as contas da família usando apenas os IDs
        all_transactions = []
        for acc_id in account_ids:
            try:
                account_transactions = await self.transaction_repository.get_by_account_id(
                    acc_id, start_date, end_date
                )
                all_transactions.extend(account_transactions)
            except Exception as e:
                print(f"⚠️ Erro ao buscar transações da conta {acc_id}: {e}")
                continue
        
        # Buscar saldos das contas usando SQL direto (evita greenlet error)
        total_balance = 0.0
        accounts = []  # Inicializar lista de contas
        if account_ids:
            try:
                balance_result = await db_session.execute(
                    text("SELECT SUM(balance) FROM accounts WHERE id = ANY(:account_ids) AND is_active = true"),
                    {"account_ids": [str(acc_id) for acc_id in account_ids]}
                )
                balance_row = balance_result.fetchone()
                if balance_row and balance_row[0]:
                    total_balance = float(balance_row[0])
                print(f"📊 Saldo total das contas: {total_balance}")
                
                # Buscar objetos Account para usar depois (apenas se necessário)
                for acc_id in account_ids:
                    try:
                        acc = await self.account_repository.get_by_id(acc_id)
                        if acc:
                            accounts.append(acc)
                    except Exception as e2:
                        print(f"⚠️ Erro ao buscar conta {acc_id}: {e2}")
                        continue
            except Exception as e:
                print(f"⚠️ Erro ao buscar saldo das contas: {e}")
                # Fallback: buscar contas individualmente
                for acc_id in account_ids:
                    try:
                        acc = await self.account_repository.get_by_id(acc_id)
                        if acc:
                            accounts.append(acc)
                            total_balance += float(acc.balance) if acc.is_active else 0
                    except Exception as e2:
                        print(f"⚠️ Erro ao buscar conta {acc_id}: {e2}")
                        continue
        
        transactions = all_transactions
        
        # Calcular totais do mês
        monthly_income = 0.0
        monthly_expenses = 0.0
        for t in transactions:
            try:
                trans_type = str(t.transaction_type.value) if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
                trans_status = str(t.status.value) if hasattr(t.status, 'value') else str(t.status)
                if trans_status == "completed":
                    amount = float(t.amount)
                    if trans_type == "income":
                        monthly_income += amount
                    elif trans_type == "expense":
                        monthly_expenses += amount
            except Exception as e:
                print(f"Erro ao processar transação {t.id}: {e}")
                continue
        monthly_savings = monthly_income - monthly_expenses
        
        # Se total_balance ainda for 0 e tivermos contas, recalcular
        if total_balance == 0 and accounts:
            total_balance = sum(float(a.balance) for a in accounts if a.is_active)
        
        # Transações recentes (últimas 10) - usar account_ids em vez de accounts
        recent_start_date = end_date - timedelta(days=90)
        all_recent_transactions = []
        for acc_id in account_ids:
            try:
                account_transactions = await self.transaction_repository.get_by_account_id(
                    acc_id, recent_start_date, end_date
                )
                all_recent_transactions.extend(account_transactions)
            except Exception as e:
                print(f"⚠️ Erro ao buscar transações recentes da conta {acc_id}: {e}")
                continue
        
        completed_transactions = []
        for t in all_recent_transactions:
            try:
                trans_status = str(t.status.value) if hasattr(t.status, 'value') else str(t.status)
                if trans_status == "completed":
                    completed_transactions.append(t)
            except Exception:
                continue
        
        recent_transactions = sorted(
            completed_transactions,
            key=lambda x: x.transaction_date,
            reverse=True
        )[:10]
        
        # Buscar nomes de contas e categorias usando SQL direto (evita lazy loading)
        account_ids_in_transactions = {t.account_id for t in recent_transactions if t.account_id}
        category_ids_in_transactions = {t.category_id for t in recent_transactions if t.category_id}
        
        accounts_dict = {}
        if account_ids_in_transactions:
            try:
                accounts_result = await db_session.execute(
                    text("SELECT id, name FROM accounts WHERE id = ANY(:account_ids)"),
                    {"account_ids": [str(aid) for aid in account_ids_in_transactions]}
                )
                for row in accounts_result.fetchall():
                    accounts_dict[row[0]] = row[1]
            except Exception as e:
                print(f"⚠️ Erro ao buscar nomes de contas: {e}")
        
        categories_dict = {}
        if category_ids_in_transactions:
            try:
                categories_result = await db_session.execute(
                    text("SELECT id, name FROM categories WHERE id = ANY(:category_ids)"),
                    {"category_ids": [str(cid) for cid in category_ids_in_transactions]}
                )
                for row in categories_result.fetchall():
                    categories_dict[row[0]] = row[1]
            except Exception as e:
                print(f"⚠️ Erro ao buscar nomes de categorias: {e}")
        
        # Converter transações para dict
        recent_transactions_data = []
        for t in recent_transactions:
            try:
                recent_transactions_data.append({
                    "id": str(t.id),
                    "description": t.description,
                    "amount": float(t.amount),
                    "transaction_type": str(t.transaction_type.value) if hasattr(t.transaction_type, 'value') else str(t.transaction_type),
                    "transaction_date": t.transaction_date.isoformat(),
                    "account_name": accounts_dict.get(t.account_id) if t.account_id else None,
                    "category_name": categories_dict.get(t.category_id) if t.category_id else None,
                })
            except Exception as e:
                print(f"⚠️ Erro ao processar transação {t.id}: {e}")
                continue
        
        return {
            "total_balance": total_balance,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "monthly_savings": monthly_savings,
            "recent_transactions": recent_transactions_data,
        }

    async def generate_summary_data(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Gera dados resumidos para dashboard"""
        # Buscar transações do período
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        
        # Buscar todas as contas
        accounts = await self.account_repository.get_by_user_id(user_id)
        
        # Calcular totais do mês (acessar enums de forma segura)
        monthly_income = 0.0
        monthly_expenses = 0.0
        for t in transactions:
            try:
                trans_type = str(t.transaction_type.value) if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
                trans_status = str(t.status.value) if hasattr(t.status, 'value') else str(t.status)
                if trans_status == "completed":
                    amount = float(t.amount)
                    if trans_type == "income":
                        monthly_income += amount
                    elif trans_type == "expense":
                        monthly_expenses += amount
            except Exception as e:
                print(f"Erro ao processar transação {t.id}: {e}")
                continue
        monthly_savings = monthly_income - monthly_expenses
        
        # Saldo total de todas as contas
        total_balance = sum(float(a.balance) for a in accounts if a.is_active)
        
        # Transações recentes (últimas 10) - buscar dos últimos 90 dias
        recent_start_date = end_date - timedelta(days=90)
        all_recent_transactions = await self.transaction_repository.get_by_user_id(
            user_id, recent_start_date, end_date
        )
        # Filtrar e ordenar transações completas
        completed_transactions = []
        for t in all_recent_transactions:
            try:
                trans_status = str(t.status.value) if hasattr(t.status, 'value') else str(t.status)
                if trans_status == "completed":
                    completed_transactions.append(t)
            except Exception:
                continue
        
        recent_transactions = sorted(
            completed_transactions,
            key=lambda x: x.transaction_date,
            reverse=True
        )[:10]
        
        # Converter transações para dict (sem acessar relacionamentos para evitar greenlet errors)
        recent_transactions_data = []
        for t in recent_transactions:
            try:
                trans_type = str(t.transaction_type.value) if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
                recent_transactions_data.append({
                    "id": str(t.id),
                    "description": t.description,
                    "amount": float(t.amount),
                    "transaction_type": trans_type,
                    "transaction_date": t.transaction_date.isoformat(),
                })
            except Exception as e:
                print(f"Erro ao converter transação {t.id}: {e}")
                continue
        
        # Contas a pagar (bills pendentes + transações pendentes, ordenadas por data)
        upcoming_bills_data = []
        try:
            from src.infrastructure.database.models.bill import BillStatus
            from src.infrastructure.database.models.transaction import TransactionStatus, TransactionType
            
            # Buscar todas as bills pendentes do usuário
            all_pending_bills = []
            if self.bill_repository:
                all_pending_bills = await self.bill_repository.get_by_user_id(
                    user_id=user_id,
                    status="pending"
                )
            
            # Buscar transações pendentes (despesas) diretamente do repositório
            # Usar search para filtrar por status
            pending_transactions_result = await self.transaction_repository.search(
                user_id=user_id,
                transaction_type="expense",
                status="pending",
                limit=100,
                offset=0
            )
            pending_expense_transactions = pending_transactions_result[0]  # Retorna (lista, total)
            print(f"[DEBUG] Transações pendentes encontradas: {len(pending_expense_transactions)}")
            for t in pending_expense_transactions:
                print(f"[DEBUG] - Transação: {t.description}, Status: {t.status}, Tipo: {t.transaction_type}, Data: {t.transaction_date}")
            
            # Converter bills para formato unificado
            now = datetime.now(pytz.UTC)
            all_items = []
            
            for bill in all_pending_bills:
                bill_due = bill.due_date.replace(tzinfo=pytz.UTC) if bill.due_date.tzinfo else bill.due_date
                is_overdue = bill_due < now
                all_items.append({
                    "id": str(bill.id),
                    "description": bill.name or bill.description or "",
                    "amount": float(bill.amount),
                    "due_date": bill.due_date.isoformat(),
                    "status": bill.status.value,
                    "is_overdue": is_overdue,
                    "type": "bill",  # Identificar como bill
                })
            
            # Converter transações pendentes para formato unificado
            for transaction in pending_expense_transactions:
                trans_date = transaction.transaction_date.replace(tzinfo=pytz.UTC) if transaction.transaction_date.tzinfo else transaction.transaction_date
                is_overdue = trans_date < now
                all_items.append({
                    "id": str(transaction.id),
                    "description": transaction.description or "",
                    "amount": float(transaction.amount),
                    "due_date": transaction.transaction_date.isoformat(),
                    "status": transaction.status.value,
                    "is_overdue": is_overdue,
                    "type": "transaction",  # Identificar como transaction
                })
            
            # Ordenar por data (vencidas primeiro, depois por data)
            all_items.sort(key=lambda x: (
                not x["is_overdue"],  # Vencidas (True) vêm antes de futuras (False)
                x["due_date"]
            ))
            
            # Pegar até 10 itens
            upcoming_bills_data = all_items[:10]
            
        except Exception as e:
            print(f"Erro ao buscar contas a pagar: {e}")
            import traceback
            traceback.print_exc()
        
        # Metas com progresso
        goals_progress_data = []
        try:
            goals = await self.goal_repository.get_by_user_id(user_id)
            for goal in goals:
                # Verificar se a meta está ativa
                if goal.status.value == "active":
                    current_amount = float(goal.current_amount)
                    target_amount = float(goal.target_amount)
                    progress_percentage = (current_amount / target_amount * 100) if target_amount > 0 else 0
                    goals_progress_data.append({
                        "id": str(goal.id),
                        "name": goal.name,
                        "current_amount": current_amount,
                        "target_amount": target_amount,
                        "progress_percentage": min(progress_percentage, 100),
                    })
        except Exception as e:
            print(f"Erro ao buscar metas: {e}")

        return {
            "total_balance": total_balance,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "monthly_savings": monthly_savings,
            "accounts_count": len([a for a in accounts if a.is_active]),
            "transactions_count": len(transactions),
            "recent_transactions": recent_transactions_data,
            "upcoming_bills": upcoming_bills_data,
            "goals_progress": goals_progress_data,
        }

    # ========== FASE 1 - MVP ==========

    async def get_executive_report(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Relatório Executivo - Dashboard com KPIs"""
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        accounts = await self.account_repository.get_by_user_id(user_id)
        
        # Calcular totais
        total_income = Decimal("0")
        total_expense = Decimal("0")
        transactions_by_type = defaultdict(int)
        
        for t in transactions:
            if hasattr(t.status, 'value') and t.status.value == "completed":
                amount = Decimal(str(t.amount))
                trans_type = t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
                if trans_type == "income":
                    total_income += amount
                elif trans_type == "expense":
                    total_expense += amount
                transactions_by_type[trans_type] += 1
        
        balance = total_income - total_expense
        savings_rate = (balance / total_income * 100) if total_income > 0 else Decimal("0")
        
        # Saldo total
        total_balance = sum(Decimal(str(a.balance)) for a in accounts if a.is_active)
        
        # Evolução de saldo (últimos 6 meses)
        balance_evolution = []
        for i in range(6):
            month_date = end_date - timedelta(days=30 * (5 - i))
            month_start = datetime(month_date.year, month_date.month, 1, tzinfo=pytz.UTC)
            if month_date.month == 12:
                month_end = datetime(month_date.year + 1, 1, 1, tzinfo=pytz.UTC) - timedelta(seconds=1)
            else:
                month_end = datetime(month_date.year, month_date.month + 1, 1, tzinfo=pytz.UTC) - timedelta(seconds=1)
            
            month_transactions = await self.transaction_repository.get_by_user_id(
                user_id, month_start, month_end
            )
            month_income = sum(
                Decimal(str(t.amount)) for t in month_transactions
                if hasattr(t.status, 'value') and t.status.value == "completed"
                and (t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)) == "income"
            )
            month_expense = sum(
                Decimal(str(t.amount)) for t in month_transactions
                if hasattr(t.status, 'value') and t.status.value == "completed"
                and (t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)) == "expense"
            )
            balance_evolution.append({
                "month": f"{month_date.month:02d}/{month_date.year}",
                "income": float(month_income),
                "expense": float(month_expense),
                "balance": float(month_income - month_expense),
            })
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "kpis": {
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "balance": float(balance),
                "savings_rate": float(savings_rate),
                "total_balance": float(total_balance),
                "transactions_count": len(transactions),
                "accounts_count": len([a for a in accounts if a.is_active]),
            },
            "balance_evolution": balance_evolution,
            "transactions_by_type": dict(transactions_by_type),
        }

    async def get_income_report(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Relatório de Receitas"""
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        
        # Filtrar apenas receitas completas
        income_transactions = [
            t for t in transactions
            if hasattr(t.status, 'value') and t.status.value == "completed"
            and (t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)) == "income"
        ]
        
        # Por categoria
        income_by_category = defaultdict(Decimal)
        income_by_account = defaultdict(Decimal)
        
        for t in income_transactions:
            amount = Decimal(str(t.amount))
            # Acessar categoria (já está eager-loaded)
            if hasattr(t, 'category') and t.category is not None:
                category_name = getattr(t.category, 'name', None) or 'Sem categoria'
                if category_name and category_name != 'Sem categoria':
                    income_by_category[category_name] += amount
            
            # Acessar conta (já está eager-loaded)
            if hasattr(t, 'account') and t.account is not None:
                account_name = getattr(t.account, 'name', None) or 'Sem conta'
                if account_name and account_name != 'Sem conta':
                    income_by_account[account_name] += amount
        
        total_income = sum(Decimal(str(t.amount)) for t in income_transactions)
        
        # Evolução mensal
        monthly_income = []
        current = start_date
        while current <= end_date:
            month_start = datetime(current.year, current.month, 1, tzinfo=pytz.UTC)
            if current.month == 12:
                month_end = datetime(current.year + 1, 1, 1, tzinfo=pytz.UTC) - timedelta(seconds=1)
            else:
                month_end = datetime(current.year, current.month + 1, 1, tzinfo=pytz.UTC) - timedelta(seconds=1)
            
            month_transactions = await self.transaction_repository.get_by_user_id(
                user_id, month_start, min(month_end, end_date)
            )
            month_total = sum(
                Decimal(str(t.amount)) for t in month_transactions
                if hasattr(t.status, 'value') and t.status.value == "completed"
                and (t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)) == "income"
            )
            monthly_income.append({
                "month": f"{current.month:02d}/{current.year}",
                "amount": float(month_total),
            })
            
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1, tzinfo=pytz.UTC)
            else:
                current = datetime(current.year, current.month + 1, 1, tzinfo=pytz.UTC)
        
        return {
            "total_income": float(total_income),
            "transactions_count": len(income_transactions),
            "by_category": [
                {"category": k, "amount": float(v), "percentage": float(v / total_income * 100) if total_income > 0 else 0}
                for k, v in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True)
            ],
            "by_account": [
                {"account": k, "amount": float(v), "percentage": float(v / total_income * 100) if total_income > 0 else 0}
                for k, v in sorted(income_by_account.items(), key=lambda x: x[1], reverse=True)
            ],
            "monthly_evolution": monthly_income,
        }

    async def get_expense_report(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Relatório de Despesas"""
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        
        # Filtrar apenas despesas completas
        expense_transactions = [
            t for t in transactions
            if hasattr(t.status, 'value') and t.status.value == "completed"
            and (t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)) == "expense"
        ]
        
        # Por categoria (Top 10)
        expense_by_category = defaultdict(Decimal)
        expense_by_account = defaultdict(Decimal)
        
        for t in expense_transactions:
            amount = Decimal(str(t.amount))
            # Acessar categoria (já está eager-loaded)
            if hasattr(t, 'category') and t.category is not None:
                category_name = getattr(t.category, 'name', None) or 'Sem categoria'
                if category_name and category_name != 'Sem categoria':
                    expense_by_category[category_name] += amount
            
            # Acessar conta (já está eager-loaded)
            if hasattr(t, 'account') and t.account is not None:
                account_name = getattr(t.account, 'name', None) or 'Sem conta'
                if account_name and account_name != 'Sem conta':
                    expense_by_account[account_name] += amount
        
        total_expense = sum(Decimal(str(t.amount)) for t in expense_transactions)
        
        # Top 10 categorias
        top_categories = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Evolução mensal
        monthly_expense = []
        current = start_date
        while current <= end_date:
            month_start = datetime(current.year, current.month, 1, tzinfo=pytz.UTC)
            if current.month == 12:
                month_end = datetime(current.year + 1, 1, 1, tzinfo=pytz.UTC) - timedelta(seconds=1)
            else:
                month_end = datetime(current.year, current.month + 1, 1, tzinfo=pytz.UTC) - timedelta(seconds=1)
            
            month_transactions = await self.transaction_repository.get_by_user_id(
                user_id, month_start, min(month_end, end_date)
            )
            month_total = sum(
                Decimal(str(t.amount)) for t in month_transactions
                if hasattr(t.status, 'value') and t.status.value == "completed"
                and (t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)) == "expense"
            )
            monthly_expense.append({
                "month": f"{current.month:02d}/{current.year}",
                "amount": float(month_total),
            })
            
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1, tzinfo=pytz.UTC)
            else:
                current = datetime(current.year, current.month + 1, 1, tzinfo=pytz.UTC)
        
        # Insights básicos
        insights = []
        if top_categories:
            top_category_name, top_category_amount = top_categories[0]
            insights.append({
                "type": "info",
                "message": f"Sua maior despesa foi em {top_category_name} (R$ {float(top_category_amount):,.2f})",
            })
        
        return {
            "total_expense": float(total_expense),
            "transactions_count": len(expense_transactions),
            "top_categories": [
                {"category": k, "amount": float(v), "percentage": float(v / total_expense * 100) if total_expense > 0 else 0}
                for k, v in top_categories
            ],
            "by_account": [
                {"account": k, "amount": float(v), "percentage": float(v / total_expense * 100) if total_expense > 0 else 0}
                for k, v in sorted(expense_by_account.items(), key=lambda x: x[1], reverse=True)
            ],
            "monthly_evolution": monthly_expense,
            "insights": insights,
        }

    async def get_categories_report(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Relatório de Categorias"""
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        
        # Filtrar apenas transações completas
        completed_transactions = [
            t for t in transactions
            if hasattr(t.status, 'value') and t.status.value == "completed"
        ]
        
        # Por categoria
        category_stats = defaultdict(lambda: {"income": Decimal("0"), "expense": Decimal("0"), "count": 0})
        
        for t in completed_transactions:
            # Acessar categoria (já está eager-loaded)
            if not hasattr(t, 'category') or t.category is None:
                category_name = 'Sem categoria'
            else:
                category_name = getattr(t.category, 'name', None) or 'Sem categoria'
            
            amount = Decimal(str(t.amount))
            trans_type = t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
            
            if trans_type == "income":
                category_stats[category_name]["income"] += amount
            elif trans_type == "expense":
                category_stats[category_name]["expense"] += amount
            category_stats[category_name]["count"] += 1
        
        # Calcular totais
        total_income = sum(s["income"] for s in category_stats.values())
        total_expense = sum(s["expense"] for s in category_stats.values())
        
        # Preparar dados
        categories_data = []
        for category_name, stats in category_stats.items():
            net = stats["income"] - stats["expense"]
            categories_data.append({
                "category": category_name,
                "income": float(stats["income"]),
                "expense": float(stats["expense"]),
                "net": float(net),
                "transactions_count": stats["count"],
                "income_percentage": float(stats["income"] / total_income * 100) if total_income > 0 else 0,
                "expense_percentage": float(stats["expense"] / total_expense * 100) if total_expense > 0 else 0,
            })
        
        # Ordenar por despesa (maior primeiro)
        categories_data.sort(key=lambda x: x["expense"], reverse=True)
        
        return {
            "categories": categories_data,
            "total_categories": len(categories_data),
            "total_income": float(total_income),
            "total_expense": float(total_expense),
        }

    # ========== FASE 2 - AVANÇADO ==========

    async def get_planning_vs_real_report(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Relatório de Planejamento vs Real"""
        # Buscar planejamento mensal
        from src.infrastructure.database.models.planning import PlanningType
        from src.infrastructure.database.models.planning import MonthlyPlanning
        
        # Buscar transações
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        
        # Calcular valores reais
        real_income = Decimal("0")
        real_expense = Decimal("0")
        
        for t in transactions:
            if hasattr(t.status, 'value') and t.status.value == "completed":
                amount = Decimal(str(t.amount))
                trans_type = t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
                if trans_type == "income":
                    real_income += amount
                elif trans_type == "expense":
                    real_expense += amount
        
        # Buscar planejamento (simplificado - buscar do monthly_budget se disponível)
        # Por enquanto, retornar estrutura básica
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "planned": {
                "income": 0.0,  # Será preenchido quando integrar com monthly_budget
                "expense": 0.0,
            },
            "real": {
                "income": float(real_income),
                "expense": float(real_expense),
            },
            "variance": {
                "income": float(real_income),  # Diferença
                "expense": float(real_expense),
            },
        }

    async def get_comparative_report(
        self, user_id: UUID, start_date: datetime, end_date: datetime, compare_period: str = "previous"
    ) -> Dict:
        """Relatório Comparativo"""
        # Período atual
        current_transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        
        # Calcular período anterior
        period_days = (end_date - start_date).days
        previous_start = start_date - timedelta(days=period_days + 1)
        previous_end = start_date - timedelta(seconds=1)
        
        previous_transactions = await self.transaction_repository.get_by_user_id(
            user_id, previous_start, previous_end
        )
        
        # Calcular totais período atual
        current_income = Decimal("0")
        current_expense = Decimal("0")
        for t in current_transactions:
            if hasattr(t.status, 'value') and t.status.value == "completed":
                amount = Decimal(str(t.amount))
                trans_type = t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
                if trans_type == "income":
                    current_income += amount
                elif trans_type == "expense":
                    current_expense += amount
        
        # Calcular totais período anterior
        previous_income = Decimal("0")
        previous_expense = Decimal("0")
        for t in previous_transactions:
            if hasattr(t.status, 'value') and t.status.value == "completed":
                amount = Decimal(str(t.amount))
                trans_type = t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
                if trans_type == "income":
                    previous_income += amount
                elif trans_type == "expense":
                    previous_expense += amount
        
        # Calcular variações
        income_variance = float(current_income - previous_income)
        expense_variance = float(current_expense - previous_expense)
        income_percentage = float((income_variance / previous_income * 100) if previous_income > 0 else 0)
        expense_percentage = float((expense_variance / previous_expense * 100) if previous_expense > 0 else 0)
        
        return {
            "current_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "income": float(current_income),
                "expense": float(current_expense),
                "balance": float(current_income - current_expense),
            },
            "previous_period": {
                "start_date": previous_start.isoformat(),
                "end_date": previous_end.isoformat(),
                "income": float(previous_income),
                "expense": float(previous_expense),
                "balance": float(previous_income - previous_expense),
            },
            "variance": {
                "income": income_variance,
                "expense": expense_variance,
                "balance": float((current_income - current_expense) - (previous_income - previous_expense)),
                "income_percentage": income_percentage,
                "expense_percentage": expense_percentage,
            },
        }

    async def get_trends_report(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Relatório de Tendências"""
        # Buscar transações do período
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        
        # Agrupar por mês
        monthly_data = defaultdict(lambda: {"income": Decimal("0"), "expense": Decimal("0"), "count": 0})
        
        for t in transactions:
            if hasattr(t.status, 'value') and t.status.value == "completed":
                month_key = f"{t.transaction_date.year}-{t.transaction_date.month:02d}"
                amount = Decimal(str(t.amount))
                trans_type = t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
                if trans_type == "income":
                    monthly_data[month_key]["income"] += amount
                elif trans_type == "expense":
                    monthly_data[month_key]["expense"] += amount
                monthly_data[month_key]["count"] += 1
        
        # Preparar dados ordenados
        trends_data = []
        for month_key in sorted(monthly_data.keys()):
            data = monthly_data[month_key]
            trends_data.append({
                "month": month_key,
                "income": float(data["income"]),
                "expense": float(data["expense"]),
                "balance": float(data["income"] - data["expense"]),
                "transactions_count": data["count"],
            })
        
        # Calcular tendências
        if len(trends_data) >= 2:
            first_income = trends_data[0]["income"]
            last_income = trends_data[-1]["income"]
            first_expense = trends_data[0]["expense"]
            last_expense = trends_data[-1]["expense"]
            
            income_trend = float((last_income - first_income) / first_income * 100) if first_income > 0 else 0
            expense_trend = float((last_expense - first_expense) / first_expense * 100) if first_expense > 0 else 0
        else:
            income_trend = 0
            expense_trend = 0
        
        return {
            "trends": trends_data,
            "income_trend": income_trend,
            "expense_trend": expense_trend,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }

    async def get_goals_report(
        self, user_id: UUID
    ) -> Dict:
        """Relatório de Metas"""
        goals = await self.goal_repository.get_by_user_id(user_id)
        
        goals_data = []
        total_target = Decimal("0")
        total_current = Decimal("0")
        
        for goal in goals:
            current_amount = Decimal(str(goal.current_amount))
            target_amount = Decimal(str(goal.target_amount))
            progress = float((current_amount / target_amount * 100) if target_amount > 0 else 0)
            
            total_target += target_amount
            total_current += current_amount
            
            # Calcular dias restantes
            days_remaining = None
            if goal.target_date:
                now = datetime.now(pytz.UTC)
                target = goal.target_date.replace(tzinfo=pytz.UTC) if goal.target_date.tzinfo else goal.target_date
                days_remaining = (target - now).days
            
            goals_data.append({
                "id": str(goal.id),
                "name": goal.name,
                "current_amount": float(current_amount),
                "target_amount": float(target_amount),
                "progress": min(progress, 100),
                "remaining": float(target_amount - current_amount),
                "status": goal.status.value if hasattr(goal.status, 'value') else str(goal.status),
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "days_remaining": days_remaining,
            })
        
        return {
            "goals": goals_data,
            "summary": {
                "total_goals": len(goals_data),
                "total_target": float(total_target),
                "total_current": float(total_current),
                "total_progress": float((total_current / total_target * 100) if total_target > 0 else 0),
            },
        }

    # ========== FASE 3 - PREMIUM ==========

    async def get_temporal_report(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Relatório de Análise Temporal"""
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        
        # Filtrar apenas despesas completas
        expense_transactions = [
            t for t in transactions
            if hasattr(t.status, 'value') and t.status.value == "completed"
            and (t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)) == "expense"
        ]
        
        # Por dia da semana
        by_weekday = defaultdict(Decimal)
        weekday_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        # Por dia do mês
        by_day = defaultdict(Decimal)
        
        for t in expense_transactions:
            amount = Decimal(str(t.amount))
            weekday = t.transaction_date.weekday()  # 0 = segunda, 6 = domingo
            day = t.transaction_date.day
            
            by_weekday[weekday] += amount
            by_day[day] += amount
        
        # Preparar dados
        weekday_data = [
            {"day": weekday_names[i], "amount": float(by_weekday[i])}
            for i in range(7)
        ]
        
        day_data = [
            {"day": day, "amount": float(by_day[day])}
            for day in sorted(by_day.keys())
        ]
        
        return {
            "by_weekday": weekday_data,
            "by_day": day_data,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }

    async def get_accounts_report(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Relatório de Contas"""
        accounts = await self.account_repository.get_by_user_id(user_id)
        transactions = await self.transaction_repository.get_by_user_id(
            user_id, start_date, end_date
        )
        
        accounts_data = []
        
        for account in accounts:
            if not account.is_active:
                continue
            
            # Calcular movimentação
            account_income = Decimal("0")
            account_expense = Decimal("0")
            account_transactions = [
                t for t in transactions
                if t.account_id == account.id
                and hasattr(t.status, 'value') and t.status.value == "completed"
            ]
            
            for t in account_transactions:
                amount = Decimal(str(t.amount))
                trans_type = t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type)
                if trans_type == "income":
                    account_income += amount
                elif trans_type == "expense":
                    account_expense += amount
            
            accounts_data.append({
                "id": str(account.id),
                "name": account.name,
                "type": account.account_type.value if hasattr(account.account_type, 'value') else str(account.account_type),
                "balance": float(Decimal(str(account.balance))),
                "income": float(account_income),
                "expense": float(account_expense),
                "transactions_count": len(account_transactions),
            })
        
        return {
            "accounts": accounts_data,
            "total_accounts": len(accounts_data),
            "total_balance": sum(a["balance"] for a in accounts_data),
        }

