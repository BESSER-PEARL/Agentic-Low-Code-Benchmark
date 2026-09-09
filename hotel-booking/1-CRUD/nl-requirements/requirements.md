# Natural-Language Requirements

## A hotel booking and stay management system
### People involved
The system keeps one uniform record for every person it deals with. For each of them it stores a unique identifying number, a first name, a family name, a phone number and an email address. Two specialised kinds of persons exist, and both reuse exactly the same personal details: employees who work for the hotel, and guests who occupy the rooms.
### Rooms
Every room is identified by its room number. Along with that, the hotel records how many people the room can hold at most, a free-text description of the room, and its standard nightly price.
### Bookings
A booking is identified by its own number and records an arrival date and a departure date. Arrival may never fall after departure, although the two may be the same day.
Each booking has one person acting as its contact, the individual who makes and is answerable for the booking. That person does not have to be one of the people sleeping in the rooms. Any individual may hold several bookings at once, or none at all.
Separately from the contact, each booking lists the guests who will actually stay. At least one guest must be listed, and there may be more. A given guest may appear on several bookings, or on none.
Each booking is also handled by exactly one employee, who is responsible for it. An employee may be responsible for many bookings at the same time, or for none.
A booking covers at least one room and may cover several. Each room is tied to zero or multiple booking records. For every room included in a booking, the system stores the price actually agreed for that room in that booking, which may differ from the room's standard price.
### How a booking's state is tracked
Two states are followed for every booking.
The first describes where the booking stands commercially. It can only be one of three things: awaiting payment, confirmed, or cancelled. A booking begins awaiting payment, becomes confirmed once the money has been settled, and becomes cancelled if it is called off.
The second describes where the stay stands physically. It can only be one of three things: the guests have not arrived yet, they have checked in, or they have checked out. Every new booking starts out with the guests not yet arrived.