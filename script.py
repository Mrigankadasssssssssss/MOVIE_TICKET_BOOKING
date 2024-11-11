import os
import time
import  psycopg2

HOST = 'localhost'
USER = 'postgres'
PW = 'Mriganka'
DB = "OOPSDB"

class Seats:
    def __init__(self):
        self.seats = [[1 for _ in range(10)] for _ in range(5)]

    def get_seat_status(self,row,seat_number):
        if row<1 or row>5 or seat_number<1 or seat_number>10:
            return -1
        return self.seats[row-1][seat_number-1]

    def reserve_seat(self,row,seat_number):
        if row<1 or row>5 or seat_number<1 or seat_number>10:
            return
        self.seats[row-1][seat_number-1] = 0

    def display(self):
        print(' ',end=' ')
        for i in range(10):
            print(f"{i+1}",end="")
        print('\n')
        for row in range(5):
            print(row + 1, end=" ")
            for col in range(10):
                if self.seats[row][col] == 1:
                    print("- ", end="")
                else:
                    print("O ", end="")
            print("|")
        print("-----------------------")

    def get_db(self, conn):
        query = "SELECT RowNumber, SeatNumber, Seat FROM Ticket"
        cursor = conn.cursor()
        cursor.execute(query)

        for row in cursor:
            row_number = int(row[0])
            seat_number = int(row[1])
            seat_status = int(row[2])
            self.seats[row_number - 1][seat_number - 1] = seat_status

        cursor.close()


def main():
    s = Seats()
    conn = psycopg2.connect(
        host = HOST,
        user=USER,
        password=PW,
        dbname=DB
    )
    if conn:
        print("Logged In Database!")
    time.sleep(3)

    cursor = conn.cursor()
    cursor.execute("""
           CREATE TABLE IF NOT EXISTS Ticket (
               RowNumber INT,
               SeatNumber INT,
               Seat INT
           )
       """)
    conn.commit()
    cursor.close()

    for row in range(1, 6):
        for seat_number in range(1, 11):
            cursor = conn.cursor()
            query = f"""
                    INSERT INTO Ticket (RowNumber, SeatNumber, Seat)
                    SELECT {row}, {seat_number}, 1 
                    WHERE NOT EXISTS (
                        SELECT 1 FROM Ticket WHERE RowNumber = {row} AND SeatNumber = {seat_number}
                    )
                """
            cursor.execute(query)
            conn.commit()
            cursor.close()
    time.sleep(3)
    # Main menu loop
    exit_program = False
    while not exit_program:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\nWelcome To Movie Ticket Booking System")
        print("******************************************")
        print("1. Reserve A Ticket")
        print("2. Exit")
        val = int(input("Enter Your Choice: "))

        if val == 1:
            s.get_db(conn)
            s.display()

            row = int(input("Enter Row (1-5): "))
            col = int(input("Enter Seat Number (1-10): "))

            if row < 1 or row > 5 or col < 1 or col > 10:
                print("Invalid Row or Seat Number!")
                time.sleep(3)
                continue

            seat_status = s.get_seat_status(row, col)
            if seat_status == -1:
                print("Invalid Row or Seat Number!")
                time.sleep(3)
                continue

            if seat_status == 0:
                print("Sorry: Seat is already reserved!")
                time.sleep(3)
                continue

            s.reserve_seat(row, col)
            update_query = f"UPDATE Ticket SET Seat = 0 WHERE RowNumber = {row} AND SeatNumber = {col}"
            cursor = conn.cursor()
            cursor.execute(update_query)
            conn.commit()
            cursor.close()

            print(f"Seat Is Reserved Successfully in Row {row} and Seat Number {col}")
            time.sleep(3)

        elif val == 2:
            exit_program = True
            print("Good Luck!")
            time.sleep(3)

        else:
            print("Invalid Input")
            time.sleep(3)

    conn.close()

if __name__ == "__main__":
    main()


