from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import database
from agents import BankError, CreditoAgent, DebitoAgent


class BankingRulesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.original_db_path = database.DB_PATH
        self.tmpdir = tempfile.TemporaryDirectory()
        database.DB_PATH = Path(self.tmpdir.name) / "test_banco.db"
        database.init_db()

    def tearDown(self) -> None:
        database.DB_PATH = self.original_db_path
        self.tmpdir.cleanup()

    def balance(self, account_number: str) -> float:
        row = database.query_one(
            "SELECT balance FROM accounts WHERE account_number = ?",
            (account_number,),
        )
        return round(float(row["balance"]), 2)

    def credit_balance(self, account_number: str) -> float:
        row = database.query_one(
            """
            SELECT cc.balance
            FROM credit_cards cc
            JOIN accounts a ON a.id = cc.account_id
            WHERE a.account_number = ?
            """,
            (account_number,),
        )
        return round(float(row["balance"]), 2)

    def test_transfer_moves_money_between_both_accounts(self) -> None:
        result = DebitoAgent().process(
            {
                "action": "transfer",
                "account_number": "1002003001",
                "target_account": "1002003002",
                "amount": 1000,
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(self.balance("1002003001"), 11500.00)
        self.assertEqual(self.balance("1002003002"), 6000.00)
        self.assertEqual(result["balance"], 11500.00)
        self.assertEqual(result["target_balance"], 6000.00)

        outgoing = database.query_one(
            """
            SELECT type, amount, related_account
            FROM transactions
            WHERE type = 'TRANSFERENCIA_SALIDA'
            ORDER BY id DESC
            LIMIT 1
            """
        )
        incoming = database.query_one(
            """
            SELECT type, amount, related_account
            FROM transactions
            WHERE type = 'TRANSFERENCIA_ENTRADA'
            ORDER BY id DESC
            LIMIT 1
            """
        )

        self.assertEqual(float(outgoing["amount"]), 1000.00)
        self.assertEqual(outgoing["related_account"], "1002003002")
        self.assertEqual(float(incoming["amount"]), 1000.00)
        self.assertEqual(incoming["related_account"], "1002003001")

    def test_insufficient_transfer_rolls_back_everything(self) -> None:
        before_source = self.balance("1002003001")
        before_target = self.balance("1002003002")

        with self.assertRaises(BankError):
            DebitoAgent().process(
                {
                    "action": "transfer",
                    "account_number": "1002003001",
                    "target_account": "1002003002",
                    "amount": 50000,
                }
            )

        self.assertEqual(self.balance("1002003001"), before_source)
        self.assertEqual(self.balance("1002003002"), before_target)

    def test_credit_payment_reduces_debit_and_credit_debt(self) -> None:
        before_debit = self.balance("1002003001")
        before_credit = self.credit_balance("1002003001")

        result = CreditoAgent().process(
            {
                "action": "payment",
                "account_number": "1002003001",
                "amount": 1000,
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(self.balance("1002003001"), before_debit - 1000)
        self.assertEqual(self.credit_balance("1002003001"), before_credit - 1000)

        movement = database.query_one(
            """
            SELECT type, amount
            FROM transactions
            WHERE type = 'PAGO_TARJETA'
            ORDER BY id DESC
            LIMIT 1
            """
        )
        self.assertEqual(float(movement["amount"]), 1000.00)

    def test_demo_balances_match_expected_start(self) -> None:
        self.assertEqual(self.balance("1002003001"), 12500.00)
        self.assertEqual(self.balance("1002003002"), 5000.00)


if __name__ == "__main__":
    unittest.main()
