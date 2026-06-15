# CineBook

CineBook is a movie ticket booking platform built with Django and MySQL. The application allows users to browse movies, view show timings, select seats, complete bookings, and access their booking history through a secure authentication system.

## Overview

The platform simulates a real-world cinema booking experience by integrating user authentication, seat management, payment tracking, and booking history. The project follows a modular Django architecture with separate applications responsible for movies, bookings, and user management.

## Features

User registration and login with password hashing using bcrypt

Session-based authentication

Movie catalog with detailed movie information

Show listings across multiple theatres and timings

Real-time seat availability tracking

Multi-seat booking support

Payment processing workflow

Booking confirmation page

Personal booking history for each user

MySQL database integration

## Project Structure

The project is organized into dedicated Django applications:

firstapp handles the landing page and general navigation

movies manages movie listings and movie details

booking handles show schedules, seat selection, payments, and bookings

users manages registration, authentication, and booking history

templates contains all HTML templates used across the application

images stores movie posters and visual assets

## Technologies Used

Python

Django

MySQL

HTML

CSS

bcrypt

## Database Design

The application uses MySQL for persistent storage.

Core entities include:

Users

Movies

Shows

Seats

Payments

Relationships are maintained through foreign keys to ensure data integrity between users, seats, and booking records.

## Booking Flow

User registers or logs into the platform

User selects a movie

Available shows are displayed

User selects one or more available seats

Payment details are submitted

Selected seats are marked as booked

Booking confirmation is displayed

Booking history becomes available under the user's account

## Security

Passwords are never stored in plain text

bcrypt hashing is used before storing credentials

Session-based authentication is used to maintain user login state

CSRF protection is enabled for form submissions

## Running the Project

Install the required dependencies

Configure database credentials inside config.py

Create the required MySQL database and tables

Run the Django development server

```bash
python manage.py runserver
```

Open the application in a browser:

```text
http://127.0.0.1:8000/
```

## Assets

Movie posters are stored inside the images directory and are used throughout the platform to enhance the browsing experience.

## Future Improvements

Online payment gateway integration

Seat locking during checkout

Email confirmations

Admin dashboard

Movie search and filtering

Responsive mobile-first interface

Booking cancellation and refund support

## Author

Hritvi Narvekar
