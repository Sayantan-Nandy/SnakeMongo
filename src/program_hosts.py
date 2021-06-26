from infrastructure.switchlang import switch
import infrastructure.state as state
import services.db_services as svc
from dateutil import parser
import datetime


def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', log_into_account)
            s.case('l', list_cages)
            s.case('r', register_cage)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case('o', logout)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('Login to your [a]ccount')
    print('[L]ist your cages')
    print('[R]egister a cage')
    print('[U]pdate cage availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print("L[O]gout")
    print()


def create_account():
    print(' ****************** REGISTER **************** ')
    
    name = input("Enter your name: ")
    email = input("Enter your email: ").strip().lower()

    acct_check = svc.check_email_exist(email)
    if acct_check:
        #print(acct_check)
        error_msg("Emails exists")
        return
    else:
        state.active_account = svc.create_account(name,email)
        success_msg("Account Created")


def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input("Enter email for login: ")

    acct_check = svc.check_email_exist(email)
    
    if acct_check:
        print("Login Succesful")
        state.active_account = acct_check

    else:
        print("Wrong Email is enterred!!!")
        
    


def register_cage():
    print(' ****************** REGISTER CAGE **************** ')
    
    if not state.active_account:
        print("Login needed to register cage")
        return
    
    name = input("Enter name of cage: ")
    price = float(input("Enter price of cage: "))
    sq_mts = float(input("Enter cage size in square meters: "))
    carpet = input("Is it carpeted [y,n]: ").lower().startswith('y')
    toys = input("Does it have toys [y,n]: ").lower().startswith('y')
    dang_snakes = input("Is dangerous snakes allowed [y,n]: ").lower().startswith('y')

    c = svc.create_cage(state.active_account,name,price,sq_mts,carpet,toys,dang_snakes)

    state.reload_account() # Reload the active account object with the modified data

    print("Cage is registered for ",{c.id})



def list_cages(supress_header=False):
    if not supress_header:
        print(' ******************     Your cages     **************** ')


    if not state.active_account:
        print("Login needed to list cages")
        return

    cages = svc.get_list_cages(state.active_account)

    for i,c in enumerate(cages):
        print(i+1,"Cage is ",c.name)
        for b in c.bookings:
            print('      * Booking: {}, {} days, booked? {}'.format(
                b.check_in_date,
                (b.check_out_date - b.check_in_date).days,
                'YES' if b.booked_date is not None else 'no'
            ))



def update_availability():
    print(' ****************** Add available date **************** ')
    
    if not state.active_account:
        print("Login needed to update cage availabilty")
        return

    list_cages(supress_header=True)

    cage_number = input("Enter cage number: ")
    if not cage_number.strip():
        error_msg('Cancelled')
        print()
        return

    cage_number = int(cage_number)

    cages = svc.get_list_cages(state.active_account)
    selected_cage = cages[cage_number-1]

    print("Cage selected is: ",selected_cage.name)


    start_date = parser.parse(
        input("Enter available date [yyyy-mm-dd]: ")
    )
    days = int(input("How many days is this block of time? "))

    svc.add_available_date(
        selected_cage,
        start_date,
        days
    )

    success_msg(f'Date added to cage {selected_cage.name}.')
    


def view_bookings():
    print(' ****************** Your bookings **************** ')

    """ 
    Prints details of all the bookings that have been done for the host.
    """

    if not state.active_account:
        error_msg("You must log in first to register a cage")
        return

    cages = svc.get_list_cages(state.active_account)

    bookings = [
        (c, b)
        for c in cages
        for b in c.bookings
        if b.booked_date is not None      # Only take the booking entries with the booking date set as others are not booked
    ]

    print("You have {} bookings.".format(len(bookings)))
    for c, b in bookings:
        print(' * Cage: {}, booked date: {}, from {} for {} days.'.format(
            c.name,
            datetime.date(b.booked_date.year, b.booked_date.month, b.booked_date.day),
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            b.duration_in_days
        ))
    
    


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(text)
    return action.strip().lower()


def logout():
    state.active_account=None


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(text)


def error_msg(text):
    print(text)
