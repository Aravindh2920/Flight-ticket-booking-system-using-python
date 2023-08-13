import os
import re
import uuid

class Flight:
  def __init__(self, id, source, destination, class_seats=None):
    self.id = id
    self.source = source
    self.destination = destination
    self.row_data =  {'Business': [0, 0, 0], 'Economy': [0, 0, 0]}
    self.class_seats = class_seats if class_seats is not None else {}
    self.booked_seats = {'Business': [0, 0, 0], 'Economy': [0, 0, 0]}
    self.booked_seat_list = {'Business': [], 'Economy': []}
    self.surge = 0
    self.base_cost = {'Business': 2000, 'Economy': 1000}

  def booking_cost(self):
    bcost = (self.surge * 200) + self.base_cost['Business']
    ecost = (self.surge * 100) + self.base_cost['Economy']
    return {'Business': bcost, 'Economy': ecost}
  
  def remaining_seats(self, cls):
    window_seats = self.class_seats[cls][0] - self.booked_seats[cls][0]
    middle_seats = self.class_seats[cls][1] - self.booked_seats[cls][1]
    aisle_seats = self.class_seats[cls][2] - self.booked_seats[cls][2]

    return [window_seats, middle_seats, aisle_seats]

  def update_seats(self, cls, user_seats):
    self.booked_seats[cls] = [a+b for a, b in zip(self.booked_seats[cls], user_seats)]
    print("\nTickets Booked")
  
  def seating_arrangement(self, cls):
    row_layout = []
    r = self.row_data[cls][:-1]
    n = self.row_data[cls][-1]
    for i in range(len(r)):
        if i==0:
            row_layout+="W"+"M"*(r[i]-2)
            if(r[i]!=1):
                row_layout+="A"
            continue
        if i==len(r)-1:
            if(r[i]!=1):
                row_layout+="A"
            row_layout+="M"*(r[i]-2)+"W"
        else:
            if(r[i]!=0):
                row_layout+="A"+"M"*(r[i]-2)
                if(r[i]>1):
                    row_layout+="A"
    seat_layout = [row_layout for _ in range(n)]
    return(seat_layout)
      
class Book:
  def __init__(self, flight, booked_seats, booked_class, booking_cost, meal_choice):
    self.booking_id = str(uuid.uuid4()).strip()
    self.booked_flight = flight
    self.booked_seats = booked_seats
    self.booked_class = booked_class
    self.booking_cost = booking_cost
    self.meal_choice = meal_choice

  def ticket(self, booking_id):
    if booking_id == self.booking_id:
      return [self.booked_flight, self.booked_seats, self.booked_class]

def seating(f, cl, seat_data):
  l = []
  for i in seat_data.split(','):
    i = re.sub("[{}]","",i)
    l.append(int(i))
  rows = l[-1]
  f.row_data[cl] = l
  no_of_window_seats = rows * 2
  if l[1] == 0:
    no_of_aisle_seats = rows * 2
  elif l[1] == 1:
    no_of_aisle_seats = rows * 3
  else:
    no_of_aisle_seats = rows * 4
  no_of_middle_seats = ((sum(l)-rows)*rows) - (no_of_window_seats + no_of_aisle_seats)
  f.class_seats[cl] = [no_of_window_seats, no_of_middle_seats, no_of_aisle_seats]

flight_list = []
ticket_list = []

path = os.getcwd() + "\Flights"
all_flights = os.listdir(path)


for flight in all_flights:
    d = flight.split('-')
    d[-1] = d[-1].replace('.txt', '')
    f = Flight(d[1], d[2], d[3])
    flight_list.append(f)

    file_path = path + f"\{flight}"
    with open(file_path, 'r') as file:
      lines = file.readlines()
      if not lines:
        lines = ''
        continue
      else:
        for line in lines:
          data = line.rstrip().split(':')
          cl = data[0].rstrip()
          seat = data[1]
          seating(f, cl, seat)
        file.close()

def display_flights():
  print(f"\nNo of flights: {len(flight_list)}\n")
  for flight in flight_list:
    print(f"Name: {flight.id}, From: {flight.source}, To: {flight.destination}")

def search_flights():
  source = input("\nEnter from: ").strip().capitalize()
  destination = input("Enter the destination: ").strip().capitalize()
  extra_filter = input("Do you want to see flights with business class alone ? Y or N: ").upper()
  for flight in flight_list:
    if source == flight.source and destination == flight.destination:
      if extra_filter == 'Y' and 'Business' in flight.class_seats and len(flight.class_seats) == 1:
          print(f"Name: {flight.id}, From: {flight.source}, To: {flight.destination}")
      elif extra_filter == 'Y':
          print("No Flights")
          return
      else:
          print(f"Name: {flight.id}, From: {flight.source}, To: {flight.destination}")
    else:
      print("No Flights")
      return
  select_flight()

def select_flight():
  user_input = input("Do you want to book? Y or N: ").upper()
  if user_input == 'Y':
    flight_id = input("Enter the flight id: ").upper()
    user_flight = None
    for flight in flight_list:
       if flight_id == flight.id:
          user_flight = flight
          break
    if user_flight == None:
      print("No Flights Found")
      return
    print("Available classes")
    for i in user_flight.class_seats.keys():
      print(f'{i}')
    flight_cls = input("Enter the class name: ").capitalize()
    if flight_cls in user_flight.class_seats.keys():
      seat_details = user_flight.remaining_seats(flight_cls)
      if sum(seat_details) == 0:
        print("No Seats Available")
        return
      print("\nAvailable Seats:")
      print(f"""1. Window Seats: {seat_details[0]}
2. Middle Seats: {seat_details[1]}
3. Aisle Seats: {seat_details[2]}
      """)
      select_seats(user_flight, flight_cls)
    else:
      print("Not a valid option")
      return
  else:
    return

def select_seats(user_flight, flight_cls):
  remaining_seats = user_flight.remaining_seats(flight_cls)
  window_seats = int(input("Enter the no of window seats required: "))
  middle_seats = int(input("Enter the no of middle seats required: "))
  aisle_seats = int(input("Enter the no of aisle seats required: "))

  user_seats = [window_seats, middle_seats, aisle_seats]

  if check_seats(user_seats, remaining_seats) == False:
    print("Enter a valid amount of seats")
    return
  
  tot_amt = calculate_amount(user_flight, user_seats, flight_cls)
  meal = "No"
  meal_choice = input("Do you want to book meal for all passengers? (Y/N):").upper()

  if(meal_choice == "Y"):
    tot_amt+=200*sum(user_seats)
    meal = "Yes"  
  book_seats(user_flight, user_seats, flight_cls, tot_amt, meal)

def calculate_amount(user_flight, user_seats, flight_cls):
  base_amount = user_flight.booking_cost()[flight_cls]
  total_amount = 0
  for i in range(len(user_seats)):
    if i == 1:
      total_amount += base_amount*user_seats[i]
    else:
      total_amount += base_amount*user_seats[i] + (100*user_seats[i])
  return(total_amount)


def book_seats(user_flight, user_seats, flight_cls, total_cost, meal_choice):
  layout = user_flight.seating_arrangement(flight_cls)
  user_seats_copy = user_seats.copy()
  i = 0
  flag = True
  act_seat_list = []
  while(sum(user_seats) != 0 and i <= 2):
    flag = True
    for row in range(len(layout)):
      for col in range(len(layout[row])):
        act_seat = f"{row+1}_{chr(col+65)}"
        if i == 0 and layout[row][col] == 'W' and user_seats[0] > 0 and act_seat not in user_flight.booked_seat_list[flight_cls]:
          user_flight.booked_seat_list[flight_cls].append(act_seat)
          act_seat_list.append(act_seat)
          user_seats[i] -= 1
        if i == 1 and layout[row][col] == 'M' and user_seats[1] > 0 and act_seat not in user_flight.booked_seat_list[flight_cls]:
          user_flight.booked_seat_list[flight_cls].append(act_seat)
          act_seat_list.append(act_seat)
          user_seats[i] -= 1
        if i == 2 and layout[row][col] == 'A' and user_seats[2] > 0 and act_seat not in user_flight.booked_seat_list[flight_cls]:
          user_flight.booked_seat_list[flight_cls].append(act_seat)
          act_seat_list.append(act_seat)
          user_seats[i] -= 1
        if user_seats[i] == 0:
          i += 1
          flag = False
          break
      if not flag:
        break
  user_flight.surge += 1
  b = Book(user_flight, act_seat_list, flight_cls, total_cost, meal_choice)
  ticket_list.append(b)
  
  user_flight.update_seats(flight_cls, user_seats_copy)
  print("\nPlease Note down the booking id for future use")
  print(f"\nBooking id: {b.booking_id}")
  print(f"Flight id: {b.booked_flight.id}")
  print(f"Booked Class: {b.booked_class}")
  print(f"Seat Numbers: {b.booked_seats}")
  print(f"Total cost: {total_cost}")
  print(f"Meal booked: {meal_choice}")

def check_seats(user_seats, remaining_seats):
  return all(user <= remaining for user, remaining in zip(user_seats, remaining_seats))

def search_tickets():
  ticket_id = input("\nEnter ticket id: ").strip()
  f = False
  for i in ticket_list:
    if i.booking_id == ticket_id:
      f = True
      print(f"\nBooking id: {i.booking_id}")
      print(f"Flight id: {i.booked_flight.id}")
      print(f"Booked Class: {i.booked_class}")
      print(f"Seat Numbers: {i.booked_seats}")
      print(f"Total amount: {i.booking_cost}")
      print(f"Meal Booked: {i.meal_choice}")
      break
  if not f:
    print("Ticket not Found")
  
def cancel_tickets():
  ticket_id = input("\nEnter ticket id: ").strip()
  f = False
  for i in ticket_list:
    if i.booking_id == ticket_id:
      f = True
      print(f"\nBooking id: {i.booking_id}")
      print(f"Flight id: {i.booked_flight.id}")
      print(f"Booked Class: {i.booked_class}")
      print(f"Seat Numbers: {i.booked_seats}")
      print(f"Total amount: {i.booking_cost}")
      print(f"Meal Booked: {i.meal_choice}")
      cancel_seat = input("\nEnter the seat no. you want to cancel: ")
      if cancel_seat in i.booked_seats:
        i.booked_seats.remove(cancel_seat)
        i.booked_flight.booked_seat_list[i.booked_class].remove(cancel_seat)
        layout = i.booked_flight.seating_arrangement(i.booked_class)
        x = cancel_seat.split("_")
        seat_type = layout[int(x[0])-1][ord(x[1])-65]
        if(seat_type == "W"):
          i.booked_flight.booked_seats[i.booked_class][0]-=1
        if(seat_type == "M"):
          i.booked_flight.booked_seats[i.booked_class][1]-=1
        if(seat_type == "A"):
          i.booked_flight.booked_seats[i.booked_class][2]-=1
        print("Seat cancelled successfully")
      else:
        print("Invalid seat no.")
        return
  if not f:
    print("Ticket not Found")
      
print("Welcome to busQ1 Flight Ticket Booking")
while True:
  try:
    user_input = int(input("""
    1. See Flight Details   
    2. Book Ticket   
    3. View Ticket     
    4. Cancel Ticket          
    5. Quit             
    \nEnter your choice: """))
  except:
    print("Enter a valid choice!")
    continue
  if user_input == 1:
    display_flights()
    continue
  if user_input == 2:
    search_flights()
    continue
  if user_input == 3:
    search_tickets()
    continue
  if user_input == 4:
    cancel_tickets()
    continue
  if user_input == 5:
    print("Thank you for using our service")
    break
