from __future__ import annotations
import json
import time
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional



DATA_FILE = "data.json"
USD_UAH_RATE = 43.2    
GOAL = 100000 



@dataclass
class Account:
    key: str
    name: str
    currency: str  
    balance: int = 0

    def __str__(self) -> str:
        return f"In {self.name} - {self.balance} {self.currency}"


# ----------------- Storage: json -----------------

class Storage:

    def __init__(self, filename: str = DATA_FILE) -> None:
        self.path = Path(filename)

    
    # Format 
    def default_data(self) -> Dict[str, Any]:
        return {
            "accounts": {
                "bank1": {"name": "Bank Account 1", "currency": "USD", "balance": 0},
                "bank2": {"name": "Bank Account 2", "currency": "UAH", "balance": 0},
                "cash":  {"name": "Cash", "currency": "USD", "balance": 0},
                "crypto":{"name": "Crypto", "currency": "USD", "balance": 0},
            },
            "history": [],  # tracking the history of balance changes by date
        }


    def load(self):

        if not self.path.exists():
            data = self.default_data()
            self.save(data)
            return data

        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)

        except (json.JSONDecodeError, OSError):
            backup = self.path.with_suffix(".corrupted.json")

            try:
                self.path.replace(backup)

            except OSError:
                pass

            data = self.default_data()
            self.save(data)
            return data

        base = self.default_data()
        data.setdefault("accounts", base["accounts"])
        data.setdefault("history", base["history"])


        for i, j in base["accounts"].items():
            data["accounts"].setdefault(i, j)

            for k in ("name", "currency", "balance"):
                data["accounts"][i].setdefault(k, j[k])

        return data

    
    def save(self, data: Dict[str, Any]) -> None:

        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)





# ----------------- Main -----------------

class Facade:

    def __init__(self) -> None:
        self.storage = Storage()



    def get_accounts(self):

        data = self.storage.load()
        accounts = {}

        for key in data["accounts"]:
            info = data["accounts"][key]
            name = info["name"]
            currency = info["currency"]
            balance = info["balance"]
            account = Account(key, name, currency, balance)
            accounts[key] = account

        return accounts
    

    def set_balance(self, key: str, new_balance: int) -> None:

        data = self.storage.load()

        if key not in data["accounts"]:
            raise KeyError(f"Unknown account: {key}")
        
        data["accounts"][key]["balance"] = int(new_balance)
        self.storage.save(data)


    def rate(self) -> float:
        if (USD_UAH_RATE):
            return USD_UAH_RATE
        else:
            return 43.3
        

    def get_totals(self) -> tuple[int, int]:

        accounts = self.get_accounts()
        rate = self.rate()

        usd_total = 0.0

        for a in accounts.values():
            if a.currency == "USD":
                usd_total += a.balance
            else:  
                usd_total += a.balance / rate

        usd_total_int = int(round(usd_total))
        uah_total_int = int(round(usd_total * rate))

        return usd_total_int, uah_total_int


    def history_update(self) -> None:
        data = self.storage.load()
        accounts = self.get_accounts()
        usd_total, uah_total= self.get_totals()

        info = {        
            "date": datetime.now().strftime("%d %B %Y"), 
            "usd_total": usd_total,
            "uah_total": uah_total,
            "accounts": {k: a.balance for k, a in accounts.items()},
        }

        data["history"].append(info)
        self.storage.save(data)


    def show_total_balance(self) -> None:
        accounts = self.get_accounts()
        usd = sum(a.balance for a in accounts.values() if a.currency == "USD")
        uah = sum(a.balance for a in accounts.values() if a.currency == "UAH")

        print("\nYou have:")
        print("-------------------")
        print(f"{usd}$ USD")
        print("-------------------")
        print(f"{uah}  UAH")
        print("-------------------")


    def show_each_platform(self) -> None:
        accounts = self.get_accounts()

        print("--------------------------------------")
        for i in ("bank1", "bank2", "cash", "crypto"):
            print(accounts[i])
            print("--------------------------------------")


    def convert_total(self) -> None:
        usd_total, uah_total = self.get_totals()
        rate = self.rate()
        print("\n------------------------------")
        print(f"Total balance in USD: {usd_total}")
        print("------------------------------")
        print(f"Total balance in UAH: {uah_total}")
        print("------------------------------")
        print(f"Rate used: 1 USD = {rate} UAH")
        print("------------------------------\n")



    def update_one_balance(self) -> None:
        accounts = self.get_accounts()

        menu = [ 
            ("Bank Account 1", "bank1"),
            ("Bank Account 2", "bank2"),
            ("Cash", "cash"),
            ("Crypto", "crypto")
        ]

        print("\nChoose account: \n-------------------")

        for i in range(len(menu)):
            print(f"{i+1} - {menu[i][0]}")
        print(f"{len(menu)+ 1} - Back")
        print("-------------------\n")
        

        while True:
            option_input = input("Enter option number: ").strip()
            if option_input.isdigit():
                option = int(option_input)
                if 1 <= option <= len(menu)+1:
                    break

            print("\nInvalid option.\n")

        if option == len(menu)+1:
            return
        else:
            key = menu[option - 1][1]

        while True:
            value = input("Enter new balance: ").strip()
            
            if not value.isdigit():
                print("Incorrect value.\n")
                continue
            
            new_balance = int(value)
            break

        self.set_account_balance(key, new_balance)
        print("\nSaved.\n")



    @staticmethod
    def safe_int(string: str):
        string = string.strip()
        if string == "":
            return None
        try:
            return int(string)
        except ValueError:
            return None


    def exit(self) -> None:
        usd_total, _ = self.get_totals()
        rest = GOAL - usd_total

        time.sleep(0.2)
        print("\nCalculating how much left...")
        time.sleep(0.4)
        print("\nJust one more second....\n")

        if (rest <= 0):
            print(f"\nCongrats!!!\n You reached your goal: {GOAL}!!!\n\n")
        else:
            time.sleep(0.2)
            print(f"\nIt's only {rest}$ left\n\n")
        
    

    def set_account_balance(self, key: str, new_balance: int) -> None:
        self.set_balance(key, new_balance)
        self.history_update()



    def main(self) -> None:
        while True:
            option = input(
                "\n1 - show total balance\n"
                "2 - show available funds on each platform\n"
                "3 - set new balance for one account\n"
                "4 - convert total balance\n"
                "\nPress any other key to exit.\nEnter your option: "
            ).strip()

            if option == "1":
                self.show_total_balance()
            elif option == "2":
                self.show_each_platform()
            elif option == "3":
                self.update_one_balance()
            elif option == "4":
                self.convert_total()
            else:
                self.exit()
                break


if __name__ == "__main__":
    Facade().main()
