import os
import sqlite3
import datetime
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)
DB_FILE = os.path.join(os.path.dirname(__file__), "hospital_demo.db")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ----------------------------------------------------------------------------
# HTML Template (Professional Full English Hospital Management System)
# ----------------------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hospital & Clinic Care Management Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        
        /* Print Stylesheet for Official Hospital Receipt */
        @media print {
            body * { visibility: hidden; }
            #receipt-printable-area, #receipt-printable-area * { visibility: visible; }
            #receipt-printable-area {
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
                margin: 0;
                padding: 1.5rem;
                background: white !important;
                color: black !important;
                box-shadow: none !important;
                border: none !important;
            }
            .no-print { display: none !important; }
        }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">

    <!-- Top Navigation Bar -->
    <header class="bg-indigo-900 text-white shadow-lg sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-16">
            <div class="flex items-center space-x-3">
                <div class="bg-indigo-600 p-2 rounded-xl flex items-center justify-center text-white text-xl shadow">
                    <i class="fa-solid fa-hospital-user"></i>
                </div>
                <div>
                    <h1 class="text-lg font-bold tracking-tight">MediCare Clinic & Hospital System</h1>
                    <p class="text-xs text-indigo-200">Patient Queue • Doctor Consultations • Instant Billing • Receipt Generator</p>
                </div>
            </div>
            <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 mr-2 animate-pulse"></span> DB Live (SQLite)
                </span>
                <button onclick="openBookingModal()" class="bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold px-4 py-2 rounded-lg shadow transition flex items-center gap-2">
                    <i class="fa-solid fa-plus"></i> New Appointment
                </button>
            </div>
        </div>
    </header>

    <!-- Navigation Tabs -->
    <!-- Navigation Tabs -->
    <nav class="bg-white border-b border-slate-200 shadow-sm sticky top-16 z-30">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-8 overflow-x-auto">
            <button onclick="switchTab('dashboard')" id="tab-btn-dashboard" class="tab-btn py-4 px-1 border-b-2 border-indigo-600 font-bold text-sm text-indigo-600 flex items-center gap-2 whitespace-nowrap">
                <i class="fa-solid fa-chart-pie"></i> Overview Dashboard
            </button>
            <button onclick="switchTab('appointments')" id="tab-btn-appointments" class="tab-btn py-4 px-1 border-b-2 border-transparent font-medium text-sm text-slate-500 hover:text-slate-800 flex items-center gap-2 whitespace-nowrap">
                <i class="fa-solid fa-calendar-check"></i> Patient Queue & Consultations
            </button>
            <button onclick="switchTab('billing')" id="tab-btn-billing" class="tab-btn py-4 px-1 border-b-2 border-transparent font-medium text-sm text-slate-500 hover:text-slate-800 flex items-center gap-2 whitespace-nowrap">
                <i class="fa-solid fa-file-invoice-dollar"></i> All Invoices & Payments
            </button>
            <button onclick="switchTab('doctors')" id="tab-btn-doctors" class="tab-btn py-4 px-1 border-b-2 border-transparent font-medium text-sm text-slate-500 hover:text-slate-800 flex items-center gap-2 whitespace-nowrap">
                <i class="fa-solid fa-user-doctor"></i> Doctors Roster
            </button>
            <button onclick="switchTab('patients')" id="tab-btn-patients" class="tab-btn py-4 px-1 border-b-2 border-transparent font-medium text-sm text-slate-500 hover:text-slate-800 flex items-center gap-2 whitespace-nowrap">
                <i class="fa-solid fa-users"></i> Patients Directory
            </button>
        </div>
    </nav>

    <!-- Main Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">

        <!-- TAB 1: OVERVIEW DASHBOARD -->
        <section id="tab-dashboard" class="space-y-8">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center justify-between">
                    <div>
                        <p class="text-xs uppercase font-semibold text-slate-400">Total Patients</p>
                        <h3 id="stat-patients" class="text-3xl font-extrabold text-slate-800 mt-1">--</h3>
                        <p class="text-xs text-emerald-600 font-medium mt-1"><i class="fa-solid fa-arrow-trend-up"></i> Registered Patients</p>
                    </div>
                    <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center text-xl">
                        <i class="fa-solid fa-hospital-user"></i>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center justify-between">
                    <div>
                        <p class="text-xs uppercase font-semibold text-slate-400">Consultations</p>
                        <h3 id="stat-appointments" class="text-3xl font-extrabold text-slate-800 mt-1">--</h3>
                        <p class="text-xs text-indigo-600 font-medium mt-1"><span id="stat-completed-apt">--</span> Completed</p>
                    </div>
                    <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center text-xl">
                        <i class="fa-solid fa-calendar-check"></i>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center justify-between">
                    <div>
                        <p class="text-xs uppercase font-semibold text-slate-400">Revenue Collected</p>
                        <h3 id="stat-collected" class="text-3xl font-extrabold text-emerald-600 mt-1">₹--</h3>
                        <p class="text-xs text-slate-500 font-medium mt-1">Gross: <span id="stat-gross" class="font-bold text-slate-700">₹--</span></p>
                    </div>
                    <div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center text-xl">
                        <i class="fa-solid fa-wallet"></i>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center justify-between">
                    <div>
                        <p class="text-xs uppercase font-semibold text-slate-400">Outstanding Balance</p>
                        <h3 id="stat-pending" class="text-3xl font-extrabold text-amber-600 mt-1">₹--</h3>
                        <p class="text-xs text-amber-700 font-medium mt-1"><i class="fa-solid fa-clock"></i> Pending Payments</p>
                    </div>
                    <div class="w-12 h-12 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center text-xl">
                        <i class="fa-solid fa-receipt"></i>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <div class="flex items-center justify-between mb-4">
                        <div>
                            <h3 class="font-bold text-slate-800 text-base">Cumulative Revenue Velocity</h3>
                            <p class="text-xs text-slate-400">SQL Running Total Window Function [SUM() OVER()]</p>
                        </div>
                        <span class="text-xs bg-indigo-50 text-indigo-700 font-semibold px-2.5 py-1 rounded-full">October 2026</span>
                    </div>
                    <div class="h-64">
                        <canvas id="chart-revenue"></canvas>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <div class="flex items-center justify-between mb-4">
                        <div>
                            <h3 class="font-bold text-slate-800 text-base">Payment Method Breakdown</h3>
                            <p class="text-xs text-slate-400">UPI, Credit/Debit Cards, Cash, & Health Insurance</p>
                        </div>
                        <span class="text-xs bg-emerald-50 text-emerald-700 font-semibold px-2.5 py-1 rounded-full">Settled Channels</span>
                    </div>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="chart-payment-methods"></canvas>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div class="p-6 border-b border-slate-100 flex justify-between items-center">
                    <div>
                        <h3 class="font-bold text-slate-800 text-base">Top Doctors Revenue Leaderboard</h3>
                        <p class="text-xs text-slate-400">Calculated via SQL DENSE_RANK() Window Function</p>
                    </div>
                    <span class="text-xs bg-indigo-50 text-indigo-700 font-semibold px-2.5 py-1 rounded-full">Top Performers</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-sm">
                        <thead class="bg-slate-50 text-slate-500 uppercase text-xs border-b border-slate-200">
                            <tr>
                                <th class="py-3 px-6">Rank</th>
                                <th class="py-3 px-6">Doctor</th>
                                <th class="py-3 px-6">Specialization</th>
                                <th class="py-3 px-6 text-center">Consultations</th>
                                <th class="py-3 px-6 text-right">Gross Revenue</th>
                                <th class="py-3 px-6 text-right">Collected Revenue</th>
                            </tr>
                        </thead>
                        <tbody id="leaderboard-table-body" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 2: PATIENT QUEUE & CONSULTATIONS WORKFLOW -->
        <section id="tab-appointments" class="hidden space-y-6">
            <!-- Filter Controls -->
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-4 rounded-2xl shadow-sm border border-slate-200">
                <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Filter Queue:</span>
                    <select id="appointment-status-filter" onchange="renderAppointments()" class="text-xs font-semibold border border-slate-300 rounded-lg px-3 py-2 bg-white text-slate-700 focus:ring-2 focus:ring-indigo-500">
                        <option value="ALL">All Patients</option>
                        <option value="WAITING">Waiting / Scheduled</option>
                        <option value="Completed">Doctor Visited (Completed)</option>
                        <option value="Cancelled">Cancelled</option>
                    </select>
                </div>
                <div class="text-xs text-slate-400 font-medium">
                    Total Appointments: <span id="queue-total-count" class="font-bold text-slate-700">0</span>
                </div>
            </div>

            <!-- Unified Appointments & Billing Table -->
            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-sm">
                        <thead class="bg-slate-50 text-slate-500 uppercase text-xs border-b border-slate-200">
                            <tr>
                                <th class="py-3.5 px-5">Slot & Code</th>
                                <th class="py-3.5 px-5">Patient Details</th>
                                <th class="py-3.5 px-5">Doctor & Dept</th>
                                <th class="py-3.5 px-5 text-center">Consultation Status</th>
                                <th class="py-3.5 px-5 text-center">Billing & Payment</th>
                                <th class="py-3.5 px-5 text-center">Bill Receipt</th>
                            </tr>
                        </thead>
                        <tbody id="appointments-table-body" class="divide-y divide-slate-100">
                            <!-- Populated via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 3: BILLING & INVOICES -->
        <section id="tab-billing" class="hidden space-y-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-slate-800 text-lg">Hospital Invoices & Payments Directory</h3>
                <p class="text-xs text-slate-400">Consolidated list of all itemized bills raised across patients</p>
            </div>

            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-sm">
                        <thead class="bg-slate-50 text-slate-500 uppercase text-xs border-b border-slate-200">
                            <tr>
                                <th class="py-3 px-6">Invoice #</th>
                                <th class="py-3 px-6">Date</th>
                                <th class="py-3 px-6">Patient</th>
                                <th class="py-3 px-6 text-right">Total Amount</th>
                                <th class="py-3 px-6 text-right">Paid Amount</th>
                                <th class="py-3 px-6 text-right">Balance Due</th>
                                <th class="py-3 px-6 text-center">Status</th>
                                <th class="py-3 px-6 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="invoices-table-body" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 4: DOCTORS -->
        <section id="tab-doctors" class="hidden space-y-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-slate-800 text-lg">Hospital Medical Specialists</h3>
                <p class="text-xs text-slate-400">Board-certified doctors categorized by clinical department</p>
            </div>
            <div id="doctors-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"></div>
        </section>

        <!-- TAB 5: PATIENTS -->
        <section id="tab-patients" class="hidden space-y-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex justify-between items-center">
                <div>
                    <h3 class="font-bold text-slate-800 text-lg">Registered Patients Directory</h3>
                    <p class="text-xs text-slate-400">Demographics, blood groups, and emergency contacts</p>
                </div>
            </div>

            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-sm">
                        <thead class="bg-slate-50 text-slate-500 uppercase text-xs border-b border-slate-200">
                            <tr>
                                <th class="py-3 px-6">Patient ID</th>
                                <th class="py-3 px-6">Patient Name</th>
                                <th class="py-3 px-6">Gender / DOB</th>
                                <th class="py-3 px-6 text-center">Blood Group</th>
                                <th class="py-3 px-6">Phone & Email</th>
                                <th class="py-3 px-6">Emergency Contact</th>
                            </tr>
                        </thead>
                        <tbody id="patients-table-body" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>
        </section>
    </main>

    <!-- Modal: Book New Appointment (WITH INTEGRATED PAYMENT OPTION) -->
    <div id="modal-booking" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4 overflow-y-auto">
        <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 space-y-4 my-8">
            <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                <h4 class="font-bold text-slate-800 text-lg flex items-center gap-2">
                    <span class="bg-indigo-100 text-indigo-700 p-2 rounded-xl text-sm"><i class="fa-solid fa-calendar-plus"></i></span>
                    Book New Consultation
                </h4>
                <button onclick="closeBookingModal()" class="text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            <form id="form-booking" onsubmit="submitBooking(event)" class="space-y-3.5">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Select Patient</label>
                    <select id="book-patient-id" required class="w-full border border-slate-300 rounded-lg p-2.5 text-sm bg-white focus:ring-2 focus:ring-indigo-500"></select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Select Doctor & Department</label>
                    <select id="book-doctor-id" onchange="updateBookingDoctorFee()" required class="w-full border border-slate-300 rounded-lg p-2.5 text-sm bg-white focus:ring-2 focus:ring-indigo-500"></select>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Appointment Date</label>
                        <input type="date" id="book-date" required class="w-full border border-slate-300 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Time Slot</label>
                        <input type="time" id="book-time" required value="10:00" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Reason for Visit / Symptoms</label>
                    <input type="text" id="book-reason" required placeholder="e.g. Regular health checkup or fever" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-indigo-500">
                </div>

                <!-- INTEGRATED PAYMENT SECTION -->
                <div class="border-t border-slate-200 pt-3 space-y-2.5">
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center justify-between">
                        <span>💳 Consultation Fee & Payment Option</span>
                        <span id="booking-fee-badge" class="text-xs bg-indigo-50 text-indigo-700 font-bold px-2 py-0.5 rounded">Fee: ₹0</span>
                    </label>
                    <div class="grid grid-cols-2 gap-3">
                        <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer hover:bg-indigo-50/50">
                            <input type="radio" name="book-pay-choice" value="LATER" checked onchange="toggleBookingPayment(false)" class="text-indigo-600 focus:ring-indigo-500">
                            <span class="text-xs font-semibold text-slate-700">Pay Later (Post Consultation)</span>
                        </label>
                        <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer hover:bg-emerald-50/50">
                            <input type="radio" name="book-pay-choice" value="NOW" onchange="toggleBookingPayment(true)" class="text-emerald-600 focus:ring-emerald-500">
                            <span class="text-xs font-extrabold text-emerald-700">Pay Now (Advance Counter)</span>
                        </label>
                    </div>

                    <!-- Payment Details (shown only if Pay Now is selected) -->
                    <div id="booking-pay-details" class="hidden bg-emerald-50/70 p-3 rounded-xl border border-emerald-200 space-y-2">
                        <div class="flex justify-between items-center text-xs">
                            <span class="font-semibold text-slate-600">Total Consultation Fee to Pay:</span>
                            <span id="booking-fee-display" class="font-extrabold text-emerald-700 text-sm">₹0.00</span>
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-slate-600 uppercase mb-1">Select Payment Channel</label>
                            <select id="book-pay-method" class="w-full border border-slate-300 rounded-lg p-2 text-xs bg-white font-semibold">
                                <option value="Cash">Cash Counter</option>
                                <option value="UPI">UPI (Google Pay, PhonePe, Paytm)</option>
                                <option value="Credit Card">Credit Card</option>
                                <option value="Debit Card">Debit Card</option>
                                <option value="Insurance">Health Insurance TPA</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div id="booking-error" class="hidden p-3 rounded-lg bg-red-50 text-red-700 text-xs font-semibold border border-red-200"></div>
                <div class="flex justify-end gap-3 pt-2">
                    <button type="button" onclick="closeBookingModal()" class="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
                    <button type="submit" id="book-submit-btn" class="px-5 py-2 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow">Confirm Booking</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: Collect Payment -->
    <div id="modal-payment" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4">
            <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                <h4 class="font-bold text-slate-800 text-lg"><i class="fa-solid fa-wallet text-emerald-600 mr-2"></i> Collect Consultation Fee</h4>
                <button onclick="closePaymentModal()" class="text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            <form id="form-payment" onsubmit="submitPayment(event)" class="space-y-4">
                <input type="hidden" id="pay-invoice-id">
                <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-1">
                    <p class="text-xs text-slate-500">Invoice: <span id="pay-inv-num" class="font-bold text-slate-800"></span></p>
                    <p class="text-xs text-slate-500">Patient: <span id="pay-patient-name" class="font-bold text-slate-800"></span></p>
                    <p class="text-xs text-slate-500">Consultation Balance Due: <span id="pay-balance-due" class="font-bold text-amber-600 text-base"></span></p>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Payment Amount (₹)</label>
                    <input type="number" step="0.01" id="pay-amount" required class="w-full border border-slate-300 rounded-lg p-2.5 text-sm font-bold text-slate-800 focus:ring-2 focus:ring-emerald-500">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Payment Channel</label>
                    <select id="pay-method" required class="w-full border border-slate-300 rounded-lg p-2.5 text-sm bg-white focus:ring-2 focus:ring-emerald-500 font-semibold">
                        <option value="Cash">Cash Counter</option>
                        <option value="UPI">UPI (Google Pay, PhonePe, Paytm)</option>
                        <option value="Credit Card">Credit Card</option>
                        <option value="Debit Card">Debit Card</option>
                        <option value="Net Banking">Net Banking</option>
                        <option value="Insurance">Health Insurance TPA</option>
                    </select>
                </div>
                <div id="payment-error" class="hidden p-3 rounded-lg bg-red-50 text-red-700 text-xs font-semibold border border-red-200"></div>
                <div class="flex justify-end gap-3 pt-2">
                    <button type="button" onclick="closePaymentModal()" class="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
                    <button type="submit" class="px-5 py-2 text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow">Collect & Mark Paid</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: Official Printable Medical Invoice / Bill Receipt -->
    <div id="modal-receipt" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4 overflow-y-auto">
        <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 space-y-6 relative my-8">
            
            <div id="receipt-printable-area" class="border border-slate-200 rounded-2xl p-6 sm:p-8 bg-white space-y-6">
                <!-- Header -->
                <div class="flex justify-between items-start border-b border-slate-200 pb-5">
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="bg-indigo-600 text-white p-2 rounded-lg text-lg"><i class="fa-solid fa-hospital"></i></span>
                            <h2 class="text-xl font-extrabold text-indigo-900">MediCare Super Specialty Hospital</h2>
                        </div>
                        <p class="text-xs text-slate-500 mt-1">Multi-Specialty Healthcare & Clinical Research Centre</p>
                        <p class="text-xs text-slate-400">Reg No: MH-2026-MED • GSTIN: 27AAAAA0000A1Z5</p>
                        <p class="text-xs text-slate-400">Phone: +91 98765 43210 • info@medicarehospital.com</p>
                    </div>
                    <div class="text-right">
                        <span id="rcpt-badge-status" class="inline-block px-3 py-1 rounded-full text-xs font-extrabold uppercase border"></span>
                        <h4 id="rcpt-inv-num" class="font-mono text-sm font-bold text-slate-700 mt-2"></h4>
                        <p id="rcpt-date" class="text-xs text-slate-500"></p>
                    </div>
                </div>

                <!-- Patient & Doctor Metadata -->
                <div class="grid grid-cols-2 gap-4 text-xs bg-slate-50 p-4 rounded-xl border border-slate-100">
                    <div>
                        <p class="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">PATIENT DETAILS</p>
                        <p id="rcpt-patient-name" class="font-bold text-slate-800 text-sm mt-0.5"></p>
                        <p id="rcpt-patient-info" class="text-slate-600 mt-0.5"></p>
                        <p id="rcpt-patient-phone" class="text-slate-600 mt-0.5"></p>
                    </div>
                    <div class="text-right sm:text-left sm:border-l sm:border-slate-200 sm:pl-4">
                        <p class="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">CONSULTING DOCTOR</p>
                        <p id="rcpt-doctor-name" class="font-bold text-slate-800 text-sm mt-0.5"></p>
                        <p id="rcpt-department" class="text-indigo-600 font-semibold mt-0.5"></p>
                        <p id="rcpt-pay-method" class="text-slate-600 mt-0.5 font-medium"></p>
                    </div>
                </div>

                <!-- Itemized Breakdown Table -->
                <div>
                    <table class="w-full text-left text-xs border-collapse">
                        <thead class="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                            <tr>
                                <th class="py-2.5 px-3">Service / Charge Description</th>
                                <th class="py-2.5 px-3 text-right">Amount (₹)</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 text-slate-700">
                            <tr>
                                <td class="py-2 px-3 font-medium">Doctor Consultation Fee</td>
                                <td id="rcpt-consultation" class="py-2 px-3 text-right font-medium">₹0.00</td>
                            </tr>
                            <tr>
                                <td class="py-2 px-3 font-medium">Clinical / Diagnostic Procedure Charges</td>
                                <td id="rcpt-procedure" class="py-2 px-3 text-right font-medium">₹0.00</td>
                            </tr>
                            <tr>
                                <td class="py-2 px-3 font-medium">Prescribed Pharmacy & Medication</td>
                                <td id="rcpt-medication" class="py-2 px-3 text-right font-medium">₹0.00</td>
                            </tr>
                            <tr>
                                <td class="py-2 px-3 text-emerald-600 font-medium">Special Privilege Discount</td>
                                <td id="rcpt-discount" class="py-2 px-3 text-right text-emerald-600 font-medium">- ₹0.00</td>
                            </tr>
                            <tr>
                                <td class="py-2 px-3 text-slate-500 font-medium">Government Healthcare Tax (GST)</td>
                                <td id="rcpt-tax" class="py-2 px-3 text-right text-slate-500 font-medium">+ ₹0.00</td>
                            </tr>
                        </tbody>
                        <tfoot class="border-t-2 border-slate-300 font-bold">
                            <tr class="text-slate-800 text-sm">
                                <td class="py-2.5 px-3">Total Invoice Bill:</td>
                                <td id="rcpt-total" class="py-2.5 px-3 text-right">₹0.00</td>
                            </tr>
                            <tr class="text-emerald-700 text-sm bg-emerald-50/50">
                                <td class="py-2 px-3">Total Amount Paid:</td>
                                <td id="rcpt-paid" class="py-2 px-3 text-right">₹0.00</td>
                            </tr>
                            <tr class="text-amber-800 text-sm bg-amber-50/50">
                                <td class="py-2 px-3">Remaining Balance Due:</td>
                                <td id="rcpt-due" class="py-2 px-3 text-right">₹0.00</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>

                <!-- Footer & Authorized Stamp -->
                <div class="flex justify-between items-end border-t border-slate-200 pt-6 text-xs text-slate-500">
                    <div>
                        <p class="font-semibold text-slate-700">Terms & Conditions:</p>
                        <p class="text-[11px] text-slate-400">1. This is a computer generated official medical invoice.</p>
                        <p class="text-[11px] text-slate-400">2. Valid for healthcare insurance claims reimbursement.</p>
                        <p class="text-[11px] text-slate-400">3. Emergency Helpline: 1800-MEDICARE</p>
                    </div>
                    <div class="text-center">
                        <div class="h-12 border-b border-dashed border-slate-300 w-36 mb-1"></div>
                        <p class="font-bold text-slate-700 text-[11px]">Authorized Cashier / TPA</p>
                        <p class="text-[10px] text-slate-400">MediCare Accounts Dept</p>
                    </div>
                </div>
            </div>

            <!-- Action Buttons (Hidden when printed) -->
            <div class="flex justify-end gap-3 no-print">
                <button type="button" onclick="closeReceiptModal()" class="px-5 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition">
                    Close
                </button>
                <button type="button" onclick="window.print()" class="px-6 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-lg transition flex items-center gap-2">
                    <i class="fa-solid fa-print"></i> Print Bill Receipt
                </button>
            </div>
        </div>
    </div>

    <!-- Frontend Script -->
    <script>
        let cachedData = { stats: null, appointments: [], invoices: [], doctors: [], patients: [] };
        let revChart = null, payChart = null;

        function switchTab(tabId) {
            document.querySelectorAll('main > section').forEach(el => el.classList.add('hidden'));
            document.getElementById('tab-' + tabId).classList.remove('hidden');

            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('border-indigo-600', 'text-indigo-600', 'font-bold');
                btn.classList.add('border-transparent', 'text-slate-500', 'font-medium');
            });
            const activeBtn = document.getElementById('tab-btn-' + tabId);
            if (activeBtn) {
                activeBtn.classList.add('border-indigo-600', 'text-indigo-600', 'font-bold');
                activeBtn.classList.remove('border-transparent', 'text-slate-500', 'font-medium');
            }

            if (tabId === 'dashboard' && cachedData && cachedData.stats) {
                renderRevenueChart(cachedData.stats.cumulative_revenue);
                renderPaymentMethodsChart(cachedData.stats.payment_channels);
            }
        }

        async function fetchAllData() {
            try {
                const [statsRes, aptsRes, invsRes, docsRes, ptsRes] = await Promise.all([
                    fetch('/api/stats').then(r => r.json()),
                    fetch('/api/appointments').then(r => r.json()),
                    fetch('/api/invoices').then(r => r.json()),
                    fetch('/api/doctors').then(r => r.json()),
                    fetch('/api/patients').then(r => r.json())
                ]);

                cachedData.stats = statsRes;
                cachedData.appointments = aptsRes;
                cachedData.invoices = invsRes;
                cachedData.doctors = docsRes;
                cachedData.patients = ptsRes;

                renderAppointments();
                renderDashboard();
                renderInvoices();
                renderDoctors();
                renderPatients();
                populateDropdowns();
            } catch (err) {
                console.error("Failed to fetch data:", err);
            }
        }

        function renderAppointments() {
            const tbody = document.getElementById('appointments-table-body');
            const filter = document.getElementById('appointment-status-filter').value;
            tbody.innerHTML = '';

            let list = cachedData.appointments;
            if (filter === 'WAITING') {
                list = list.filter(a => a.status === 'Scheduled' || a.status === 'Confirmed');
            } else if (filter !== 'ALL') {
                list = list.filter(a => a.status === filter);
            }

            document.getElementById('queue-total-count').innerText = list.length;

            list.forEach(a => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50/80 transition';

                // Checkup Status & Action
                let checkupHtml = '';
                if (a.status === 'Scheduled' || a.status === 'Confirmed') {
                    checkupHtml = `
                        <div class="flex flex-col items-center gap-1.5">
                            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                                ⏳ Waiting for Doctor
                            </span>
                            <button onclick="markPatientSeen(${a.appointment_id}, '${a.patient_name.replace("'", "")}')" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow-sm transition flex items-center gap-1.5">
                                <i class="fa-solid fa-circle-check"></i> ✓ Mark Completed
                            </button>
                        </div>
                    `;
                } else if (a.status === 'Completed') {
                    checkupHtml = `
                        <div class="text-center">
                            <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300">
                                <i class="fa-solid fa-check-double text-emerald-600"></i> Doctor Visited (Completed)
                            </span>
                        </div>
                    `;
                } else if (a.status === 'Cancelled') {
                    checkupHtml = `
                        <div class="text-center">
                            <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700 border border-red-200">
                                ✕ Cancelled
                            </span>
                        </div>
                    `;
                } else {
                    checkupHtml = `<div class="text-center text-xs text-slate-400 font-semibold">${a.status}</div>`;
                }

                // Billing & Pay Action
                let billingHtml = '';
                if (a.payment_status === 'Paid') {
                    billingHtml = `
                        <div class="text-center">
                            <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-300">
                                <i class="fa-solid fa-circle-check text-emerald-600"></i> ₹${(a.total_amount || 0).toLocaleString('en-IN')} (PAID)
                            </span>
                        </div>
                    `;
                } else if (a.invoice_id && (a.balance_due > 0 || a.payment_status === 'Unpaid' || a.payment_status === 'Partially Paid')) {
                    billingHtml = `
                        <div class="flex flex-col items-center gap-1.5">
                            <span class="text-xs font-bold text-amber-700">Due: ₹${(a.balance_due || a.total_amount).toLocaleString('en-IN')}</span>
                            <button onclick="openPaymentModal(${a.invoice_id}, '${a.invoice_number}', '${a.patient_name.replace("'", "")}', ${a.balance_due || a.total_amount})" class="bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold px-3 py-1 rounded-lg shadow-sm transition flex items-center gap-1">
                                <i class="fa-solid fa-wallet"></i> 💵 Collect Payment
                            </button>
                        </div>
                    `;
                } else if (a.status === 'Completed' && !a.invoice_id) {
                    billingHtml = `
                        <div class="text-center">
                            <button onclick="markPatientSeen(${a.appointment_id}, '${a.patient_name.replace("'", "")}')" class="text-indigo-600 font-bold text-xs underline">
                                Generate Bill
                            </button>
                        </div>
                    `;
                } else {
                    billingHtml = `
                        <div class="text-center">
                            <span class="text-xs text-slate-400">Due: ₹${a.consultation_fee}</span>
                        </div>
                    `;
                }

                // Receipt Action Button
                let receiptHtml = '';
                if (a.invoice_id) {
                    receiptHtml = `
                        <div class="text-center">
                            <button onclick="openReceiptModal(${a.invoice_id})" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-bold px-3 py-1.5 rounded-lg transition inline-flex items-center gap-1.5 shadow-sm" title="Print Official Bill Receipt">
                                <i class="fa-solid fa-print"></i> 🖨️ Bill Print
                            </button>
                        </div>
                    `;
                } else {
                    receiptHtml = `<div class="text-center text-xs text-slate-300">Pending Bill</div>`;
                }

                tr.innerHTML = `
                    <td class="py-3.5 px-5">
                        <div class="font-mono text-xs font-bold text-indigo-600">${a.appointment_number}</div>
                        <div class="text-slate-800 font-semibold text-xs mt-0.5">${a.appointment_date}</div>
                        <div class="text-slate-400 text-[11px]">${a.appointment_time}</div>
                    </td>
                    <td class="py-3.5 px-5">
                        <div class="font-bold text-slate-800 text-sm">${a.patient_name}</div>
                        <div class="text-xs text-slate-500 mt-0.5"><i class="fa-solid fa-phone text-slate-400 mr-1 text-[10px]"></i>${a.patient_phone || 'N/A'}</div>
                        <div class="text-xs text-slate-400 italic truncate max-w-xs mt-0.5">${a.reason_for_visit || 'General Consultation'}</div>
                    </td>
                    <td class="py-3.5 px-5">
                        <div class="font-semibold text-slate-800 text-xs">${a.doctor_name}</div>
                        <div class="text-[11px] text-indigo-600 font-medium">${a.specialization_name}</div>
                        <div class="text-[11px] text-slate-400">Fee: ₹${a.consultation_fee}</div>
                    </td>
                    <td class="py-3.5 px-5">${checkupHtml}</td>
                    <td class="py-3.5 px-5">${billingHtml}</td>
                    <td class="py-3.5 px-5">${receiptHtml}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function markPatientSeen(appointmentId, patientName) {
            if (!confirm(`Has the doctor completed the consultation for ${patientName}?\\n\\nClicking OK will mark status as 'Doctor Visited' and automatically generate the billing invoice.`)) {
                return;
            }

            try {
                const res = await fetch('/api/appointments/complete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ appointment_id: appointmentId })
                });

                const data = await res.json();
                if (!res.ok) {
                    alert(data.error || 'Failed to update status');
                    return;
                }

                await fetchAllData();

                if (data.invoice_id && data.balance_due > 0) {
                    if (confirm(`✅ Consultation completed for ${patientName}!\\n\\nDoctor consultation invoice for ₹${data.total_amount} has been generated.\\nWould you like to collect fee payment now?`)) {
                        openPaymentModal(data.invoice_id, data.invoice_number, patientName, data.balance_due);
                    }
                }
            } catch (err) {
                console.error(err);
                alert('Connection error');
            }
        }

        function renderDashboard() {
            const { stats } = cachedData;
            if (!stats) return;

            document.getElementById('stat-patients').innerText = stats.total_patients;
            document.getElementById('stat-appointments').innerText = stats.total_appointments;
            document.getElementById('stat-completed-apt').innerText = stats.completed_appointments;
            document.getElementById('stat-gross').innerText = '₹' + stats.gross_revenue.toLocaleString('en-IN');
            document.getElementById('stat-collected').innerText = '₹' + stats.collected_revenue.toLocaleString('en-IN');
            document.getElementById('stat-pending').innerText = '₹' + stats.pending_balance.toLocaleString('en-IN');

            renderRevenueChart(stats.cumulative_revenue);
            renderPaymentMethodsChart(stats.payment_channels);
            renderLeaderboard(stats.doctor_leaderboard);
        }

        function renderRevenueChart(revenueData) {
            const ctx = document.getElementById('chart-revenue').getContext('2d');
            if (revChart) revChart.destroy();

            const labels = revenueData.map(d => d.payment_day);
            const data = revenueData.map(d => d.cumulative_revenue_to_date);

            revChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Cumulative Collected (₹)',
                        data: data,
                        borderColor: '#4f46e5',
                        backgroundColor: 'rgba(79, 70, 229, 0.08)',
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#4f46e5',
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            ticks: { callback: v => '₹' + v.toLocaleString('en-IN') },
                            grid: { color: '#f1f5f9' }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        function renderPaymentMethodsChart(channelsData) {
            const ctx = document.getElementById('chart-payment-methods').getContext('2d');
            if (payChart) payChart.destroy();

            const labels = channelsData.map(d => d.payment_method);
            const data = channelsData.map(d => d.total_amount);

            payChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#64748b']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                    }
                }
            });
        }

        function renderLeaderboard(leaderboard) {
            const tbody = document.getElementById('leaderboard-table-body');
            tbody.innerHTML = '';
            leaderboard.forEach(d => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50 transition';
                tr.innerHTML = `
                    <td class="py-3 px-6 font-bold text-indigo-600">#${d.revenue_rank}</td>
                    <td class="py-3 px-6 font-semibold text-slate-800">${d.doctor_name}</td>
                    <td class="py-3 px-6"><span class="bg-indigo-50 text-indigo-700 text-xs px-2.5 py-1 rounded-full font-medium">${d.specialization_name}</span></td>
                    <td class="py-3 px-6 text-center font-bold text-slate-700">${d.total_consultations}</td>
                    <td class="py-3 px-6 text-right font-semibold text-slate-700">₹${d.total_revenue_generated.toLocaleString('en-IN')}</td>
                    <td class="py-3 px-6 text-right font-bold text-emerald-600">₹${d.total_revenue_collected.toLocaleString('en-IN')}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderInvoices() {
            const tbody = document.getElementById('invoices-table-body');
            tbody.innerHTML = '';

            cachedData.invoices.forEach(inv => {
                let badge = 'bg-red-100 text-red-700';
                if (inv.payment_status === 'Paid') badge = 'bg-emerald-100 text-emerald-700';
                else if (inv.payment_status === 'Partially Paid') badge = 'bg-amber-100 text-amber-700';

                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50 transition';
                tr.innerHTML = `
                    <td class="py-3 px-6 font-mono text-xs font-bold text-slate-700">${inv.invoice_number}</td>
                    <td class="py-3 px-6 text-slate-600">${inv.invoice_date}</td>
                    <td class="py-3 px-6 font-semibold text-slate-800">${inv.patient_name}</td>
                    <td class="py-3 px-6 text-right font-medium text-slate-700">₹${inv.total_amount.toLocaleString('en-IN')}</td>
                    <td class="py-3 px-6 text-right font-bold text-emerald-600">₹${inv.paid_amount.toLocaleString('en-IN')}</td>
                    <td class="py-3 px-6 text-right font-bold text-amber-600">₹${inv.balance_due.toLocaleString('en-IN')}</td>
                    <td class="py-3 px-6 text-center"><span class="px-2.5 py-1 rounded-full text-xs font-semibold ${badge}">${inv.payment_status}</span></td>
                    <td class="py-3 px-6 text-center space-x-2 whitespace-nowrap">
                        ${inv.balance_due > 0 ? `
                        <button onclick="openPaymentModal(${inv.invoice_id}, '${inv.invoice_number}', '${inv.patient_name.replace("'", "")}', ${inv.balance_due})" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow transition">
                            <i class="fa-solid fa-wallet mr-1"></i> 💵 Pay
                        </button>` : ''}
                        <button onclick="openReceiptModal(${inv.invoice_id})" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-bold px-3 py-1.5 rounded-lg transition" title="Print Bill Receipt">
                            <i class="fa-solid fa-print mr-1"></i> 🖨️ Bill Print
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderDoctors() {
            const grid = document.getElementById('doctors-grid');
            grid.innerHTML = '';

            cachedData.doctors.forEach(d => {
                const card = document.createElement('div');
                card.className = 'bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between';
                card.innerHTML = `
                    <div>
                        <div class="flex items-start justify-between">
                            <div>
                                <span class="bg-indigo-50 text-indigo-700 text-xs px-2.5 py-0.5 rounded-full font-semibold">${d.specialization_name}</span>
                                <h4 class="font-bold text-slate-800 text-lg mt-2">${d.doctor_name}</h4>
                                <p class="text-xs text-slate-500">${d.qualification}</p>
                            </div>
                            <span class="px-2 py-0.5 rounded-full text-xs font-semibold ${d.status === 'Active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'}">${d.status}</span>
                        </div>
                        <div class="mt-4 pt-4 border-t border-slate-100 space-y-1 text-xs text-slate-600">
                            <div><i class="fa-solid fa-briefcase text-slate-400 mr-1.5"></i> Experience: <b>${d.experience_years} years</b></div>
                            <div><i class="fa-solid fa-phone text-slate-400 mr-1.5"></i> ${d.phone}</div>
                            <div><i class="fa-solid fa-envelope text-slate-400 mr-1.5"></i> ${d.email}</div>
                        </div>
                    </div>
                    <div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                        <span class="text-xs text-slate-400">Consultation Fee</span>
                        <span class="text-base font-extrabold text-indigo-600">₹${d.consultation_fee}</span>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        function renderPatients() {
            const tbody = document.getElementById('patients-table-body');
            tbody.innerHTML = '';

            cachedData.patients.forEach(p => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50 transition';
                tr.innerHTML = `
                    <td class="py-3 px-6 font-mono text-xs font-semibold text-slate-500">PT-${String(p.patient_id).padStart(4, '0')}</td>
                    <td class="py-3 px-6 font-semibold text-slate-800">${p.first_name} ${p.last_name}</td>
                    <td class="py-3 px-6 text-slate-600">${p.gender} • ${p.dob}</td>
                    <td class="py-3 px-6 text-center"><span class="bg-red-50 text-red-700 font-bold text-xs px-2 py-0.5 rounded-md border border-red-200">${p.blood_group || 'N/A'}</span></td>
                    <td class="py-3 px-6 text-xs text-slate-600">
                        <div><i class="fa-solid fa-phone mr-1 text-slate-400"></i>${p.phone}</div>
                        <div class="text-slate-400">${p.email || ''}</div>
                    </td>
                    <td class="py-3 px-6 text-xs text-slate-600">
                        <div class="font-semibold text-slate-700">${p.emergency_contact_name || 'N/A'}</div>
                        <div class="text-slate-400">${p.emergency_contact_phone || ''}</div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function populateDropdowns() {
            const ptSelect = document.getElementById('book-patient-id');
            ptSelect.innerHTML = '<option value="">-- Choose Patient --</option>';
            cachedData.patients.forEach(p => {
                ptSelect.innerHTML += `<option value="${p.patient_id}">${p.first_name} ${p.last_name} (${p.phone})</option>`;
            });

            const docSelect = document.getElementById('book-doctor-id');
            docSelect.innerHTML = '<option value="">-- Choose Doctor --</option>';
            cachedData.doctors.filter(d => d.status === 'Active').forEach(d => {
                docSelect.innerHTML += `<option value="${d.doctor_id}" data-fee="${d.consultation_fee}">${d.doctor_name} - ${d.specialization_name} (Fee: ₹${d.consultation_fee})</option>`;
            });

            const today = new Date().toISOString().split('T')[0];
            document.getElementById('book-date').value = today;
            updateBookingDoctorFee();
        }

        function updateBookingDoctorFee() {
            const docSelect = document.getElementById('book-doctor-id');
            const selectedOpt = docSelect.options[docSelect.selectedIndex];
            const fee = selectedOpt ? selectedOpt.getAttribute('data-fee') || '0' : '0';
            document.getElementById('booking-fee-badge').innerText = 'Fee: ₹' + fee;
            document.getElementById('booking-fee-display').innerText = '₹' + fee;
        }

        function toggleBookingPayment(isPayNow) {
            const payBox = document.getElementById('booking-pay-details');
            const submitBtn = document.getElementById('book-submit-btn');
            if (isPayNow) {
                payBox.classList.remove('hidden');
                submitBtn.innerText = "Confirm Booking & Collect Fee";
                submitBtn.className = "px-5 py-2 text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow";
            } else {
                payBox.classList.add('hidden');
                submitBtn.innerText = "Confirm Booking";
                submitBtn.className = "px-5 py-2 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow";
            }
        }

        function openBookingModal() {
            document.getElementById('booking-error').classList.add('hidden');
            document.querySelector('input[name="book-pay-choice"][value="LATER"]').checked = true;
            toggleBookingPayment(false);
            document.getElementById('modal-booking').classList.remove('hidden');
        }

        function closeBookingModal() {
            document.getElementById('modal-booking').classList.add('hidden');
        }

        async function submitBooking(e) {
            e.preventDefault();
            const payChoice = document.querySelector('input[name="book-pay-choice"]:checked').value;
            const isPayNow = (payChoice === 'NOW');

            const payload = {
                patient_id: parseInt(document.getElementById('book-patient-id').value),
                doctor_id: parseInt(document.getElementById('book-doctor-id').value),
                appointment_date: document.getElementById('book-date').value,
                appointment_time: document.getElementById('book-time').value + ':00',
                reason_for_visit: document.getElementById('book-reason').value,
                pay_now: isPayNow,
                payment_method: document.getElementById('book-pay-method').value
            };

            const res = await fetch('/api/appointments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await res.json();
            if (!res.ok) {
                const errBox = document.getElementById('booking-error');
                errBox.innerText = result.error || 'Failed to book appointment';
                errBox.classList.remove('hidden');
            } else {
                closeBookingModal();
                await fetchAllData();
                switchTab('appointments');

                // If Paid right now, immediately pop up the receipt!
                if (result.invoice_id) {
                    openReceiptModal(result.invoice_id);
                }
            }
        }

        function openPaymentModal(invoiceId, invNum, patientName, balanceDue) {
            document.getElementById('payment-error').classList.add('hidden');
            document.getElementById('pay-invoice-id').value = invoiceId;
            document.getElementById('pay-inv-num').innerText = invNum;
            document.getElementById('pay-patient-name').innerText = patientName;
            document.getElementById('pay-balance-due').innerText = '₹' + balanceDue.toLocaleString('en-IN');
            document.getElementById('pay-amount').value = balanceDue;
            document.getElementById('modal-payment').classList.remove('hidden');
        }

        function closePaymentModal() {
            document.getElementById('modal-payment').classList.add('hidden');
        }

        async function submitPayment(e) {
            e.preventDefault();
            const invoiceId = parseInt(document.getElementById('pay-invoice-id').value);
            const payload = {
                invoice_id: invoiceId,
                amount_paid: parseFloat(document.getElementById('pay-amount').value),
                payment_method: document.getElementById('pay-method').value
            };

            const res = await fetch('/api/payments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await res.json();
            if (!res.ok) {
                const errBox = document.getElementById('payment-error');
                errBox.innerText = result.error || 'Failed to record payment';
                errBox.classList.remove('hidden');
            } else {
                closePaymentModal();
                await fetchAllData();
                switchTab('appointments');
                openReceiptModal(invoiceId);
            }
        }

        function openReceiptModal(invoiceId) {
            const inv = cachedData.invoices.find(item => item.invoice_id === invoiceId);
            if (!inv) return;

            document.getElementById('rcpt-inv-num').innerText = inv.invoice_number;
            document.getElementById('rcpt-date').innerText = 'Date: ' + inv.invoice_date;
            document.getElementById('rcpt-patient-name').innerText = inv.patient_name;
            document.getElementById('rcpt-patient-info').innerText = 'Patient ID: PT-' + String(inv.patient_id || '').padStart(4, '0') + ' • ' + (inv.patient_gender || 'General');
            document.getElementById('rcpt-patient-phone').innerText = 'Phone: ' + (inv.patient_phone || 'N/A');

            document.getElementById('rcpt-doctor-name').innerText = inv.doctor_name || 'Dr. Medical Consultant';
            document.getElementById('rcpt-department').innerText = 'Dept: ' + (inv.specialization_name || 'General Healthcare');
            document.getElementById('rcpt-pay-method').innerText = 'Payment Channel: ' + (inv.last_payment_method || 'Cash / Counter');

            // Amounts
            document.getElementById('rcpt-consultation').innerText = '₹' + (inv.consultation_fee || 0).toLocaleString('en-IN');
            document.getElementById('rcpt-procedure').innerText = '₹' + (inv.procedure_charges || 0).toLocaleString('en-IN');
            document.getElementById('rcpt-medication').innerText = '₹' + (inv.medication_charges || 0).toLocaleString('en-IN');
            document.getElementById('rcpt-discount').innerText = '- ₹' + (inv.discount_amount || 0).toLocaleString('en-IN');
            document.getElementById('rcpt-tax').innerText = '+ ₹' + (inv.tax_amount || 0).toLocaleString('en-IN');

            document.getElementById('rcpt-total').innerText = '₹' + (inv.total_amount || 0).toLocaleString('en-IN');
            document.getElementById('rcpt-paid').innerText = '₹' + (inv.paid_amount || 0).toLocaleString('en-IN');
            document.getElementById('rcpt-due').innerText = '₹' + (inv.balance_due || 0).toLocaleString('en-IN');

            // Badge
            const badge = document.getElementById('rcpt-badge-status');
            badge.innerText = inv.payment_status;
            if (inv.payment_status === 'Paid') {
                badge.className = 'inline-block px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-emerald-100 text-emerald-800 border border-emerald-300';
            } else if (inv.payment_status === 'Partially Paid') {
                badge.className = 'inline-block px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-amber-100 text-amber-800 border border-amber-300';
            } else {
                badge.className = 'inline-block px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-red-100 text-red-800 border border-red-300';
            }

            document.getElementById('modal-receipt').classList.remove('hidden');
        }

        function closeReceiptModal() {
            document.getElementById('modal-receipt').classList.add('hidden');
        }

        window.addEventListener('DOMContentLoaded', fetchAllData);
    </script>
</body>
</html>
"""

# ----------------------------------------------------------------------------
# Routes & API Endpoints
# ----------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/stats")
def get_stats():
    conn = get_db()
    cur = conn.cursor()

    total_patients = cur.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    total_appointments = cur.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    completed_appointments = cur.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Completed'").fetchone()[0]
    
    fin = cur.execute("""
        SELECT 
            COALESCE(SUM(total_amount), 0.0) AS gross_revenue,
            COALESCE(SUM(paid_amount), 0.0) AS collected_revenue,
            COALESCE(SUM(total_amount - paid_amount), 0.0) AS pending_balance
        FROM invoices
    """).fetchone()

    rev_rows = cur.execute("""
        SELECT 
            DATE(p.payment_date) AS payment_day,
            SUM(p.amount_paid) AS daily_collection,
            SUM(SUM(p.amount_paid)) OVER (ORDER BY DATE(p.payment_date)) AS cumulative_revenue_to_date
        FROM payments p
        WHERE p.payment_status = 'Success'
        GROUP BY DATE(p.payment_date)
        ORDER BY payment_day
    """).fetchall()

    channel_rows = cur.execute("""
        SELECT 
            payment_method,
            SUM(amount_paid) AS total_amount
        FROM payments
        WHERE payment_status = 'Success'
        GROUP BY payment_method
        ORDER BY total_amount DESC
    """).fetchall()

    leaderboard_rows = cur.execute("""
        SELECT 
            d.doctor_id,
            'Dr. ' || d.first_name || ' ' || d.last_name AS doctor_name,
            s.specialization_name,
            COUNT(DISTINCT a.appointment_id) AS total_consultations,
            COALESCE(SUM(i.total_amount), 0.0) AS total_revenue_generated,
            COALESCE(SUM(i.paid_amount), 0.0) AS total_revenue_collected,
            DENSE_RANK() OVER (ORDER BY COALESCE(SUM(i.total_amount), 0) DESC) AS revenue_rank
        FROM doctors d
        JOIN specializations s ON d.specialization_id = s.specialization_id
        LEFT JOIN appointments a ON d.doctor_id = a.doctor_id AND a.status = 'Completed'
        LEFT JOIN invoices i ON a.appointment_id = i.appointment_id
        GROUP BY d.doctor_id, d.first_name, d.last_name, s.specialization_name
        ORDER BY revenue_rank
        LIMIT 6
    """).fetchall()

    conn.close()

    return jsonify({
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "gross_revenue": fin["gross_revenue"],
        "collected_revenue": fin["collected_revenue"],
        "pending_balance": fin["pending_balance"],
        "cumulative_revenue": [dict(r) for r in rev_rows],
        "payment_channels": [dict(r) for r in channel_rows],
        "doctor_leaderboard": [dict(r) for r in leaderboard_rows]
    })

@app.route("/api/appointments", methods=["GET", "POST"])
def appointments():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        data = request.json or {}
        patient_id = data.get("patient_id")
        doctor_id = data.get("doctor_id")
        appointment_date = data.get("appointment_date")
        appointment_time = data.get("appointment_time")
        reason = data.get("reason_for_visit", "")
        pay_now = data.get("pay_now", False)
        payment_method = data.get("payment_method", "Cash")

        existing = cur.execute("""
            SELECT COUNT(*) FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ? AND status IN ('Scheduled', 'Confirmed')
        """, (doctor_id, appointment_date, appointment_time)).fetchone()[0]

        if existing > 0:
            conn.close()
            return jsonify({"error": "This doctor already has a booking at the selected time slot."}), 400

        new_num = f"APT-{datetime.date.today().strftime('%Y%m%d')}-{datetime.datetime.now().strftime('%f')[:4]}"

        cur.execute("""
            INSERT INTO appointments (appointment_number, patient_id, doctor_id, appointment_date, appointment_time, status, reason_for_visit)
            VALUES (?, ?, ?, ?, ?, 'Scheduled', ?)
        """, (new_num, patient_id, doctor_id, appointment_date, appointment_time, reason))
        
        appointment_id = cur.lastrowid
        invoice_id = None

        if pay_now:
            doc = cur.execute("SELECT consultation_fee FROM doctors WHERE doctor_id = ?", (doctor_id,)).fetchone()
            fee = doc["consultation_fee"] if doc else 500.0

            inv_num = f"INV-{datetime.date.today().strftime('%Y%m%d')}-{datetime.datetime.now().strftime('%f')[:4]}"
            cur.execute("""
                INSERT INTO invoices (
                    invoice_number, appointment_id, patient_id, invoice_date,
                    consultation_fee, total_amount, paid_amount, payment_status, due_date
                ) VALUES (?, ?, ?, CURRENT_DATE, ?, ?, ?, 'Paid', CURRENT_DATE)
            """, (inv_num, appointment_id, patient_id, fee, fee, fee))
            
            invoice_id = cur.lastrowid

            pay_ref = f"PAY-{datetime.date.today().strftime('%Y%m%d')}-{datetime.datetime.now().strftime('%f')[:4]}"
            cur.execute("""
                INSERT INTO payments (payment_reference, invoice_id, payment_date, amount_paid, payment_method, payment_status)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, 'Success')
            """, (pay_ref, invoice_id, fee, payment_method))

        conn.commit()
        conn.close()
        return jsonify({
            "message": "Appointment booked successfully!", 
            "appointment_number": new_num,
            "invoice_id": invoice_id
        })

    rows = cur.execute("""
        SELECT 
            a.appointment_id,
            a.appointment_number,
            a.appointment_date,
            a.appointment_time,
            a.status,
            a.reason_for_visit,
            p.patient_id,
            p.first_name || ' ' || p.last_name AS patient_name,
            p.phone AS patient_phone,
            'Dr. ' || d.first_name || ' ' || d.last_name AS doctor_name,
            s.specialization_name,
            d.consultation_fee,
            i.invoice_id,
            i.invoice_number,
            i.total_amount,
            i.paid_amount,
            (i.total_amount - i.paid_amount) AS balance_due,
            COALESCE(i.payment_status, 'No Bill') AS payment_status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN specializations s ON d.specialization_id = s.specialization_id
        LEFT JOIN invoices i ON a.appointment_id = i.appointment_id
        ORDER BY a.appointment_date DESC, a.appointment_time ASC
    """).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/appointments/complete", methods=["POST"])
def complete_appointment():
    data = request.json or {}
    appointment_id = data.get("appointment_id")
    if not appointment_id:
        return jsonify({"error": "Appointment ID required"}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute("UPDATE appointments SET status = 'Completed' WHERE appointment_id = ?", (appointment_id,))

    inv = cur.execute("SELECT invoice_id, invoice_number, total_amount, paid_amount FROM invoices WHERE appointment_id = ?", (appointment_id,)).fetchone()
    
    if inv:
        invoice_id = inv["invoice_id"]
        inv_number = inv["invoice_number"]
        total_amount = inv["total_amount"]
        balance_due = inv["total_amount"] - inv["paid_amount"]
    else:
        apt = cur.execute("""
            SELECT a.patient_id, d.consultation_fee 
            FROM appointments a 
            JOIN doctors d ON a.doctor_id = d.doctor_id 
            WHERE a.appointment_id = ?
        """, (appointment_id,)).fetchone()

        if not apt:
            conn.close()
            return jsonify({"error": "Appointment not found"}), 404

        patient_id = apt["patient_id"]
        fee = apt["consultation_fee"]
        inv_number = f"INV-{datetime.date.today().strftime('%Y%m%d')}-{datetime.datetime.now().strftime('%f')[:4]}"

        cur.execute("""
            INSERT INTO invoices (
                invoice_number, appointment_id, patient_id, invoice_date,
                consultation_fee, total_amount, paid_amount, payment_status, due_date
            ) VALUES (?, ?, ?, CURRENT_DATE, ?, ?, 0.0, 'Unpaid', DATE('now', '+7 days'))
        """, (inv_number, appointment_id, patient_id, fee, fee))

        invoice_id = cur.lastrowid
        total_amount = fee
        balance_due = fee

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Patient marked as Visited / Completed successfully!",
        "appointment_id": appointment_id,
        "invoice_id": invoice_id,
        "invoice_number": inv_number,
        "total_amount": total_amount,
        "balance_due": balance_due
    })

@app.route("/api/invoices")
def invoices():
    conn = get_db()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT 
            i.invoice_id,
            i.invoice_number,
            i.invoice_date,
            i.consultation_fee,
            i.procedure_charges,
            i.medication_charges,
            i.discount_amount,
            i.tax_amount,
            i.total_amount,
            i.paid_amount,
            (i.total_amount - i.paid_amount) AS balance_due,
            i.payment_status,
            p.patient_id,
            p.first_name || ' ' || p.last_name AS patient_name,
            p.phone AS patient_phone,
            p.gender AS patient_gender,
            'Dr. ' || d.first_name || ' ' || d.last_name AS doctor_name,
            s.specialization_name,
            (SELECT payment_method FROM payments WHERE invoice_id = i.invoice_id ORDER BY payment_id DESC LIMIT 1) AS last_payment_method
        FROM invoices i
        JOIN patients p ON i.patient_id = p.patient_id
        JOIN appointments a ON i.appointment_id = a.appointment_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN specializations s ON d.specialization_id = s.specialization_id
        ORDER BY i.invoice_date DESC
    """).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/payments", methods=["POST"])
def payments():
    data = request.json or {}
    invoice_id = data.get("invoice_id")
    amount_paid = float(data.get("amount_paid", 0.0))
    payment_method = data.get("payment_method", "Cash")

    if amount_paid <= 0:
        return jsonify({"error": "Payment amount must be greater than zero."}), 400

    conn = get_db()
    cur = conn.cursor()

    inv = cur.execute("SELECT total_amount, paid_amount FROM invoices WHERE invoice_id = ?", (invoice_id,)).fetchone()
    if not inv:
        conn.close()
        return jsonify({"error": "Invoice not found."}), 404

    total_amount = inv["total_amount"]
    current_paid = inv["paid_amount"]
    balance_due = total_amount - current_paid

    if amount_paid > balance_due + 0.01:
        conn.close()
        return jsonify({"error": f"Payment amount (₹{amount_paid}) cannot exceed balance due (₹{balance_due})."}), 400

    pay_ref = f"PAY-{datetime.date.today().strftime('%Y%m%d')}-{datetime.datetime.now().strftime('%f')[:4]}"

    cur.execute("""
        INSERT INTO payments (payment_reference, invoice_id, payment_date, amount_paid, payment_method, payment_status)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, 'Success')
    """, (pay_ref, invoice_id, amount_paid, payment_method))

    new_paid = current_paid + amount_paid
    new_status = "Paid" if new_paid >= total_amount - 0.01 else "Partially Paid"

    cur.execute("""
        UPDATE invoices SET paid_amount = ?, payment_status = ? WHERE invoice_id = ?
    """, (new_paid, new_status, invoice_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Payment recorded successfully!", "payment_reference": pay_ref, "new_status": new_status})

@app.route("/api/doctors")
def doctors():
    conn = get_db()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT 
            d.doctor_id,
            'Dr. ' || d.first_name || ' ' || d.last_name AS doctor_name,
            s.specialization_name,
            d.qualification,
            d.experience_years,
            d.consultation_fee,
            d.status,
            d.email,
            d.phone
        FROM doctors d
        JOIN specializations s ON d.specialization_id = s.specialization_id
        ORDER BY s.specialization_name, d.first_name
    """).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/patients")
def patients():
    conn = get_db()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT 
            patient_id, first_name, last_name, dob, gender, blood_group,
            phone, email, emergency_contact_name, emergency_contact_phone
        FROM patients
        ORDER BY patient_id ASC
    """).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*70)
    print("  🏥 MediCare Hospital & Clinic Management System")
    print(f"  Server running on: http://127.0.0.1:{port}")
    print("="*70 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)
