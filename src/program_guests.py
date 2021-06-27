from infrastructure.switchlang import switch
import program_hosts as hosts
import infrastructure.state as state
import services.db_services as svc
from dateutil import parser

def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_snake)
            s.case('y', view_your_snakes)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case('o', hosts.logout)

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a snake')
    print('View [y]our snakes')
    print('[V]iew your bookings')
    print('L[O]gout')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_snake():
    print(' ****************** Add a snake **************** ')
    

    if not state.active_account:
        print("Login needed to register snake")
        return
    
    name = input("Enter the name of snake: ")
    species = input("Enter the species: ")
    length = float(input("Enter length of snake: "))
    is_venom = input("Is the snake venomous: ").lower().startswith('y')

    s = svc.create_snake(state.active_account,name,species,length,is_venom)

    state.reload_account() # Reload the active account object with the modified data

    print("Snake is registered is ",{s.id})



def view_your_snakes():
    print(' ****************** Your snakes **************** ')

    if not state.active_account:
        print("Login needed to view snakes")
        return

    snakes = svc.get_snake_list(state.active_account)


    for i,s in enumerate(snakes):
        print(i+1,"Snake name is ",s.name)
    



def book_a_cage():
    print(' ****************** Book a cage **************** ')
    

    if not state.active_account:
        print("Login needed to book a cage")
        return
    
    snakes = svc.get_snake_list(state.active_account)

    if snakes == []:
        print("Please add snake to proceed")
        return
    
    else:
        for i,s in enumerate(snakes):
            print(i+1,"Snake name is ",s.name)
    
    snake_number = int(input("Selected your snake: "))
    selected_snake = snakes[snake_number-1]

    start_date = parser.parse(
        input("Enter check-in date [yyyy-mm-dd]: ")
    )

    end_date = parser.parse(
        input("Enter check-out date [yyyy-mm-dd]: ")
    )
    
    if start_date>end_date:
        print("Checkout date is before checkin date")
        return

    cages = svc.get_available_cages(selected_snake,start_date,end_date)

    
    if cages == []:
        print("No available cages for those dates")
        return

    for i,c in enumerate(cages):
        print(i+1,c.name,"is available","is carpeted: ",c.is_carpeted,"has toys: ",c.has_toys)

    cage_number = int(input("Which cage do you want? "))

    cage = cages[cage_number-1]
    svc.book_cage_for_snake(state.active_account,selected_snake,cage,start_date,end_date)

    print("Booking Done for",selected_snake.name,"in cage",cage.name)
    



def view_bookings():
    print(' ****************** Your bookings **************** ')

    if not state.active_account:
        print("Login needed to view bookings")
        return
    
    snakes = svc.get_snake_list(state.active_account)

    snakes_in_cages = svc.get_bookings(snakes)

    for s,cages in snakes_in_cages:
        for c in cages:
            for b in c.bookings:
                if b.guest_snake_id==s.id:
                    print("Snake is {} in cage {} from {} to {}".format(s.name,c.name,b.check_in_date.strftime('%Y-%m-%d'),b.check_out_date.strftime('%Y-%m-%d')))
