#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WooCommerce Product Uploader with Claude AI
Simple local web application for uploading products to WooCommerce
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from requests.auth import HTTPBasicAuth
import base64
import time
import csv
import io
import os
from typing import Dict, List, Optional
from image_search_square_only import fetch_square_product_images as fetch_product_image_from_retailers

app = Flask(__name__)
CORS(app)

# Create temporary images directory
TEMP_IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'temp_images')
os.makedirs(TEMP_IMAGES_DIR, exist_ok=True)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>העלאת מוצרים אוטומטית - MyBikeStore</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #2563eb;
            --primary-dark: #1e40af;
            --success: #10b981;
            --error: #ef4444;
            --warning: #f59e0b;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-light: #64748b;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        }

        body {
            font-family: 'Heebo', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
            color: var(--text);
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        .header {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
            text-align: center;
        }

        .header h1 {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }

        .header p {
            color: var(--text-light);
            font-size: 1rem;
        }

        .status-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: var(--success);
            color: white;
            border-radius: 20px;
            font-size: 0.875rem;
            margin-top: 1rem;
        }

        .tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .tab-button {
            flex: 1;
            padding: 1rem 2rem;
            background: var(--card-bg);
            border: 2px solid transparent;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            color: var(--text);
            box-shadow: var(--shadow);
        }

        .tab-button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .tab-button.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary-dark);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: var(--shadow-lg);
            margin-bottom: 2rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--text);
        }

        input, textarea, select {
            width: 100%;
            padding: 0.875rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 1rem;
            font-family: 'Heebo', sans-serif;
            transition: all 0.2s;
            background: white;
        }

        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        textarea {
            resize: vertical;
            min-height: 100px;
        }

        .button {
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-family: 'Heebo', sans-serif;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            justify-content: center;
        }

        .button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .button-primary {
            background: var(--primary);
            color: white;
        }

        .button-primary:hover:not(:disabled) {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .button-secondary {
            background: var(--bg);
            color: var(--text);
            border: 2px solid var(--border);
        }

        .button-success {
            background: var(--success);
            color: white;
        }

        .button-success:hover:not(:disabled) {
            background: #059669;
        }

        .button-group {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }

        .preview-section {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 2px solid var(--border);
        }

        .preview-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            text-align: center;
            color: var(--text);
        }

        .preview-image {
            background: var(--bg);
            border: 2px dashed var(--border);
            border-radius: 8px;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            overflow: hidden;
        }

        .category-tree {
            max-height: 400px;
            overflow-y: auto;
            border: 2px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            background: white;
            direction: rtl;
        }

        .category-item {
            margin-bottom: 0.5rem;
        }

        .category-parent {
            display: flex;
            align-items: center;
            padding: 0.5rem;
            cursor: pointer;
            border-radius: 6px;
            transition: background 0.2s;
            user-select: none;
        }

        .category-parent:hover {
            background: var(--bg);
        }

        .category-parent input[type="checkbox"] {
            width: auto;
            margin-left: 0.5rem;
            cursor: pointer;
        }

        .category-parent label {
            flex: 1;
            font-weight: 600;
            margin: 0;
            cursor: pointer;
        }

        .toggle-icon {
            margin-left: 0.5rem;
            font-size: 0.8rem;
            transition: transform 0.2s;
            color: var(--text-secondary);
        }

        .toggle-icon.expanded {
            transform: rotate(180deg);
        }

        .category-children {
            margin-right: 2rem;
            display: none;
        }

        .category-children.expanded {
            display: block;
        }

        .category-child {
            display: flex;
            align-items: center;
            padding: 0.4rem 0.5rem;
            border-radius: 4px;
            transition: background 0.2s;
        }

        .category-child:hover {
            background: var(--bg);
        }

        .category-child input[type="checkbox"] {
            width: auto;
            margin-left: 0.5rem;
            cursor: pointer;
        }

        .category-child label {
            flex: 1;
            font-weight: normal;
            margin: 0;
            cursor: pointer;
            color: var(--text);
        }

        .category-child label::before {
            content: "→ ";
            color: var(--text-secondary);
        }

        .preview-image {
            width: 300px;
            height: 300px;
            margin: 0 auto 1.5rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg);
            overflow: hidden;
        }

        .preview-image img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .preview-image.empty {
            color: var(--text-light);
            font-size: 1rem;
        }

        .char-counter {
            text-align: left;
            font-size: 0.875rem;
            color: var(--text-light);
            margin-top: 0.25rem;
        }

        .char-counter.warning {
            color: var(--warning);
        }

        .char-counter.error {
            color: var(--error);
        }

        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .alert-success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #6ee7b7;
        }

        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
        }

        .alert-info {
            background: #dbeafe;
            color: #1e40af;
            border: 1px solid #93c5fd;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .csv-upload {
            border: 3px dashed var(--border);
            border-radius: 12px;
            padding: 3rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: var(--bg);
        }

        .csv-upload:hover {
            border-color: var(--primary);
            background: white;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--border);
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--success));
            transition: width 0.3s ease;
            border-radius: 4px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }

        .stat-card {
            background: var(--bg);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }

        .stat-label {
            font-size: 0.875rem;
            color: var(--text-light);
            margin-top: 0.25rem;
        }

        .hidden {
            display: none !important;
        }

        .setup-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            backdrop-filter: blur(5px);
        }

        .setup-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 2rem;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.3);
        }

        .info-box {
            background: #eff6ff;
            border: 1px solid #93c5fd;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-size: 0.875rem;
        }

        .example-csv {
            background: #f1f5f9;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
            margin: 1rem 0;
            direction: ltr;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚴 העלאת מוצרים אוטומטית</h1>
            <p>MyBikeStore.co.il - מערכת חכמה עם AI מלא של Claude</p>
            <div class="status-badge">🤖 AI מחובר ופעיל</div>
            <button onclick="openSettings()" style="position: absolute; top: 1rem; left: 1rem; padding: 0.5rem 1rem; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem;">
                ⚙️ הגדרות
            </button>
        </div>

        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('manual')">
                📝 הוספה ידנית
            </button>
            <button class="tab-button" onclick="switchTab('csv')">
                📊 העלאה מ-CSV
            </button>
        </div>

        <!-- Tab 1: Manual Entry -->
        <div id="manual-tab" class="tab-content active">
            <div class="card">
                <h2 style="margin-bottom: 1.5rem; font-size: 1.5rem;">הוספת מוצר בודד</h2>
                
                <div id="manual-alert"></div>

                <div class="form-group">
                    <label>שם המוצר (עברית או אנגלית) *</label>
                    <input type="text" id="product-name" placeholder="שמן שרשרת אופניים Squirt">
                </div>

                <div class="form-group">
                    <label>מחיר (₪) *</label>
                    <input type="number" id="product-price" step="0.01" placeholder="89.90">
                </div>

                <div class="form-group">
                    <label>קטגוריות * (בחר קטגוריה אחת או יותר)</label>
                    <div class="category-tree" id="category-tree">
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="Uncategorized" id="cat-uncategorized">
                                <label for="cat-uncategorized"><strong>Uncategorized</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="Gift Card" id="cat-giftcard">
                                <label for="cat-giftcard"><strong>Gift Card</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="Shimano" id="cat-shimano">
                                <label for="cat-shimano"><strong>Shimano</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="SRAM" id="cat-sram">
                                <label for="cat-sram"><strong>SRAM</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent" onclick="toggleCategory(event, 'avizirim')">
                                <input type="checkbox" name="categories" value="אביזרים" id="cat-avizirim" onclick="event.stopPropagation()">
                                <label for="cat-avizirim"><strong>אביזרים</strong></label>
                                <span class="toggle-icon" id="toggle-avizirim">▼</span>
                            </div>
                            <div class="category-children" id="children-avizirim">
                                <div class="category-child"><input type="checkbox" name="categories" value="אורות" id="cat-orot"><label for="cat-orot">אורות</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="בקבוקים וכלובי בקבוק" id="cat-bakbukim"><label for="cat-bakbukim">בקבוקים וכלובי בקבוק</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="גריפים" id="cat-gripim"><label for="cat-gripim">גריפים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="מחזיקי טלפון" id="cat-machzikei"><label for="cat-machzikei">מחזיקי טלפון</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="מנעולים לאופניים" id="cat-manalim"><label for="cat-manalim">מנעולים לאופניים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="משאבות לאופניים" id="cat-mishabot"><label for="cat-mishabot">משאבות לאופניים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="מתלים לאופניים" id="cat-matalim"><label for="cat-matalim">מתלים לאופניים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="צמיגים לאופניים" id="cat-tzmigirim"><label for="cat-tzmigirim">צמיגים לאופניים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="תוספות מעשיות" id="cat-tosafot"><label for="cat-tosafot">תוספות מעשיות</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="תיקים וכיסוים" id="cat-tikim"><label for="cat-tikim">תיקים וכיסוים</label></div>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="אוזן למעביר אחורי" id="cat-ozen">
                                <label for="cat-ozen"><strong>אוזן למעביר אחורי</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="אופני איזון" id="cat-izun">
                                <label for="cat-izun"><strong>אופני איזון</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent" onclick="toggleCategory(event, 'ofanaim')">
                                <input type="checkbox" name="categories" value="אופניים" id="cat-ofanaim" onclick="event.stopPropagation()">
                                <label for="cat-ofanaim"><strong>אופניים</strong></label>
                                <span class="toggle-icon" id="toggle-ofanaim">▼</span>
                            </div>
                            <div class="category-children" id="children-ofanaim">
                                <div class="category-child"><input type="checkbox" name="categories" value="אופני הרים" id="cat-harim"><label for="cat-harim">אופני הרים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="אופני ילדים" id="cat-yeladim"><label for="cat-yeladim">אופני ילדים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="אופני עיר" id="cat-ir"><label for="cat-ir">אופני עיר</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="אופניים חשמליים" id="cat-chashmalim"><label for="cat-chashmalim">אופניים חשמליים</label></div>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent" onclick="toggleCategory(event, 'chalakim')">
                                <input type="checkbox" name="categories" value="חלקי אופניים" id="cat-chalakim" onclick="event.stopPropagation()">
                                <label for="cat-chalakim"><strong>חלקי אופניים</strong></label>
                                <span class="toggle-icon" id="toggle-chalakim">▼</span>
                            </div>
                            <div class="category-children" id="children-chalakim">
                                <div class="category-child"><input type="checkbox" name="categories" value="אוכפים לאופניים" id="cat-ochafim"><label for="cat-ochafim">אוכפים לאופניים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="בוטום בראקט" id="cat-bottom"><label for="cat-bottom">בוטום בראקט</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="ברקסים" id="cat-brakes"><label for="cat-brakes">ברקסים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="גלגל שיניים לאופניים" id="cat-galgal"><label for="cat-galgal">גלגל שיניים לאופניים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="גלגלים וחישוקים" id="cat-glalim"><label for="cat-glalim">גלגלים וחישוקים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="חלקים לחשמלי" id="cat-chashmal-parts"><label for="cat-chashmal-parts">חלקים לחשמלי</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="חלקים קטנים" id="cat-ktanim"><label for="cat-ktanim">חלקים קטנים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="כבלים" id="cat-cables"><label for="cat-cables">כבלים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="מערכות הנעה" id="cat-hanaa"><label for="cat-hanaa">מערכות הנעה</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="סטמים" id="cat-stems"><label for="cat-stems">סטמים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="פדלים לאופניים" id="cat-pedalim"><label for="cat-pedalim">פדלים לאופניים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="פנימיות ופנצ'רים" id="cat-pnimiot"><label for="cat-pnimiot">פנימיות ופנצ'רים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="צירים" id="cat-tzirim"><label for="cat-tzirim">צירים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="שיפטרים לאופניים" id="cat-shifters"><label for="cat-shifters">שיפטרים לאופניים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="שרשראות לאופניים" id="cat-chains"><label for="cat-chains">שרשראות לאופניים</label></div>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="כיסא תינוק לאופניים" id="cat-kise">
                                <label for="cat-kise"><strong>כיסא תינוק לאופניים</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="כלים, תחזוקה ושמנים" id="cat-kelim">
                                <label for="cat-kelim"><strong>כלים, תחזוקה ושמנים</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent" onclick="toggleCategory(event, 'levush')">
                                <input type="checkbox" name="categories" value="לבוש וקסדות" id="cat-levush" onclick="event.stopPropagation()">
                                <label for="cat-levush"><strong>לבוש וקסדות</strong></label>
                                <span class="toggle-icon" id="toggle-levush">▼</span>
                            </div>
                            <div class="category-children" id="children-levush">
                                <div class="category-child"><input type="checkbox" name="categories" value="כפפות" id="cat-kfafot"><label for="cat-kfafot">כפפות</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="מגנים לאופניים" id="cat-maginim"><label for="cat-maginim">מגנים לאופניים</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="נעלי רכיבה" id="cat-naalim"><label for="cat-naalim">נעלי רכיבה</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="קסדות לאופניים" id="cat-kasda-ofanaim"><label for="cat-kasda-ofanaim">קסדות לאופניים</label></div>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="מבצעים" id="cat-mivtzaim">
                                <label for="cat-mivtzaim"><strong>מבצעים</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="מנעולי קריפטונייט" id="cat-kryptonite">
                                <label for="cat-kryptonite"><strong>מנעולי קריפטונייט</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="סוללה 60 וולט" id="cat-battery60">
                                <label for="cat-battery60"><strong>סוללה 60 וולט</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="סוללות לאופניים חשמליים" id="cat-batteries">
                                <label for="cat-batteries"><strong>סוללות לאופניים חשמליים</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="פנסים לאופניים" id="cat-pansim">
                                <label for="cat-pansim"><strong>פנסים לאופניים</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="קורקינט חשמלי" id="cat-korkinit-chashmal">
                                <label for="cat-korkinit-chashmal"><strong>קורקינט חשמלי</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent" onclick="toggleCategory(event, 'korkinitim')">
                                <input type="checkbox" name="categories" value="קורקינטים" id="cat-korkinitim" onclick="event.stopPropagation()">
                                <label for="cat-korkinitim"><strong>קורקינטים</strong></label>
                                <span class="toggle-icon" id="toggle-korkinitim">▼</span>
                            </div>
                            <div class="category-children" id="children-korkinitim">
                                <div class="category-child"><input type="checkbox" name="categories" value="סקייטבורד" id="cat-skateboard"><label for="cat-skateboard">סקייטבורד</label></div>
                                <div class="category-child"><input type="checkbox" name="categories" value="קורקינט ילדים" id="cat-korkinit-yeladim"><label for="cat-korkinit-yeladim">קורקינט ילדים</label></div>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="קסדה לקורקינט" id="cat-kasda-korkinit">
                                <label for="cat-kasda-korkinit"><strong>קסדה לקורקינט</strong></label>
                            </div>
                        </div>
                        <div class="category-item">
                            <div class="category-parent">
                                <input type="checkbox" name="categories" value="קסדות לילדים" id="cat-kasda-yeladim">
                                <label for="cat-kasda-yeladim"><strong>קסדות לילדים</strong></label>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>ביטויי מפתח לSEO (הפרד עם ,) *</label>
                    <input type="text" id="product-keywords" placeholder="שמן שרשרת, שעווה, יבש">
                </div>

                <div class="form-group" style="margin-top: 1rem;">
                    <label style="display: flex; align-items: center; cursor: pointer; user-select: none;">
                        <input type="checkbox" id="israeli-product" style="margin-left: 0.5rem; width: auto; cursor: pointer;">
                        <span>🇮🇱 מוצר ישראלי (חפש רק באתרים ישראליים)</span>
                    </label>
                </div>

                <div class="button-group">
                    <button class="button button-primary" onclick="generateContent()" id="generate-btn">
                        <span>🤖 יצירת תוכן עם AI</span>
                    </button>
                </div>

                <div id="preview-section" class="preview-section hidden">
                    <div class="preview-title">─────── תצוגה מקדימה ───────</div>

                    <div class="form-group">
                        <label>📸 תמונת המוצר</label>
                        <div class="preview-image empty" id="preview-image">
                            תמונה תופיע כאן לאחר היצירה
                        </div>
                        <div id="change-image-container" style="text-align: center; margin-top: 1rem; display: none;">
                            <button class="button button-secondary" onclick="changeImage()" id="change-image-btn" style="padding: 0.75rem 1.5rem;">
                                🔄 שנה תמונה (<span id="image-counter">1/1</span>)
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>📝 כותרת SEO</label>
                        <input type="text" id="seo-title">
                    </div>

                    <div class="form-group">
                        <label>📄 תיאור מוצר (SEO)</label>
                        <textarea id="product-description" rows="6"></textarea>
                    </div>

                    <div class="form-group">
                        <label>🏷️ Meta Description (150 תווים)</label>
                        <textarea id="meta-description" rows="3" maxlength="150"></textarea>
                        <div class="char-counter" id="char-counter">0/150 תווים</div>
                    </div>

                    <div class="form-group">
                        <label>🔑 Focus Keyphrase (Yoast)</label>
                        <input type="text" id="focus-keyphrase" readonly>
                    </div>

                    <div class="button-group">
                        <button class="button button-success" onclick="uploadProduct()" id="upload-btn">
                            📤 העלה למחסן WooCommerce
                        </button>
                        <button class="button button-secondary" onclick="clearForm()">
                            🔄 נקה טופס
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab 2: CSV Upload -->
        <div id="csv-tab" class="tab-content">
            <div class="card">
                <h2 style="margin-bottom: 1.5rem; font-size: 1.5rem;">העלאה מרובה מ-CSV</h2>
                
                <div id="csv-alert"></div>

                <div class="info-box">
                    <strong>📋 פורמט CSV נדרש:</strong><br>
                    שם המוצר, מחיר, קטגוריה, ביטויי מפתח
                </div>

                <div class="example-csv">
שם המוצר,מחיר,קטגוריה,ביטויי מפתח
שמן שרשרת Squirt,89.90,שמנים,שמן|שעווה|יבש
Continental GP5000,150,צמיגים,צמיג|כביש|Continental
                </div>

                <div class="csv-upload" onclick="document.getElementById('csv-file').click()">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
                    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">
                        לחץ לבחירת קובץ CSV
                    </div>
                    <div style="color: var(--text-light);">
                        פורמט נתמך: .csv
                    </div>
                    <input type="file" id="csv-file" accept=".csv" style="display: none;" onchange="handleCSVUpload(event)">
                </div>

                <div id="csv-processing" class="hidden">
                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-value" id="csv-total">0</div>
                            <div class="stat-label">סה"כ מוצרים</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" style="color: var(--success);" id="csv-completed">0</div>
                            <div class="stat-label">✅ הושלם</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" style="color: var(--error);" id="csv-failed">0</div>
                            <div class="stat-label">❌ נכשל</div>
                        </div>
                    </div>

                    <div class="progress-bar">
                        <div class="progress-fill" id="csv-progress" style="width: 0%"></div>
                    </div>

                    <div id="csv-current-product" class="info-box" style="display:none;">
                        <strong id="csv-current-text">מעבד...</strong>
                    </div>

                    <div class="button-group">
                        <button class="button button-primary" onclick="processCSV()" id="csv-process-btn">
                            ▶️ התחל עיבוד
                        </button>
                        <button class="button button-secondary" onclick="resetCSV()">
                            ❌ בטל
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Setup Overlay -->
    <div id="setup-overlay" class="setup-overlay">
        <div class="setup-card">
            <h2>🔧 הגדרת מערכת</h2>
            
            <div class="form-group">
                <label>כתובת האתר שלך *</label>
                <input type="text" id="site-url" placeholder="https://mybikestore.co.il">
            </div>

            <div class="form-group">
                <label>WooCommerce Consumer Key *</label>
                <input type="text" id="consumer-key" placeholder="ck_********************************">
            </div>

            <div class="form-group">
                <label>WooCommerce Consumer Secret *</label>
                <input type="password" id="consumer-secret" placeholder="cs_********************************">
            </div>

            <div class="form-group">
                <label>Anthropic API Key (Claude) *</label>
                <input type="password" id="anthropic-key" placeholder="sk-ant-********************************">
                <small style="color: var(--text-light); display: block; margin-top: 0.5rem;">
                    קבל מפתח ב: <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a>
                </small>
            </div>

            <div class="form-group">
                <label>Google API Key (לחיפוש תמונות) *</label>
                <input type="password" id="google-api-key" placeholder="AIza********************************">
                <small style="color: var(--text-light); display: block; margin-top: 0.5rem;">
                    קבל מפתח ב: <a href="https://console.cloud.google.com" target="_blank">console.cloud.google.com</a>
                </small>
            </div>

            <div class="form-group">
                <label>Google Search Engine ID *</label>
                <input type="text" id="google-search-id" placeholder="d3ce19f2989024684">
                <small style="color: var(--text-light); display: block; margin-top: 0.5rem;">
                    צור מנוע חיפוש ב: <a href="https://programmablesearchengine.google.com" target="_blank">programmablesearchengine.google.com</a>
                </small>
            </div>

            <div class="info-box">
                🔒 כל המפתחות נשמרים רק במחשב שלך ולא נשלחים לשום מקום אחר
            </div>

            <button class="button button-success" onclick="saveSettings()" style="width: 100%;">
                ✅ שמור הגדרות והתחל
            </button>
        </div>
    </div>

    <script>
        let config = null;
        let csvData = [];
        let currentImageUrl = null;
        let originalImageUrl = null;
        let alternativeImages = [];
        let currentImageIndex = 0;

        window.onload = function() {
            loadSettings();
        };

        // Toggle category children
        function toggleCategory(event, categoryId) {
            event.stopPropagation();
            const children = document.getElementById('children-' + categoryId);
            const toggle = document.getElementById('toggle-' + categoryId);
            
            if (children.classList.contains('expanded')) {
                children.classList.remove('expanded');
                toggle.classList.remove('expanded');
            } else {
                children.classList.add('expanded');
                toggle.classList.add('expanded');
            }
        }

        // Get selected categories as comma-separated string
        function getSelectedCategories() {
            const checkboxes = document.querySelectorAll('#category-tree input[name="categories"]:checked');
            const categories = Array.from(checkboxes).map(cb => cb.value);
            return categories.join(',');
        }

        function switchTab(tab) {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            if (tab === 'manual') {
                document.querySelector('.tab-button:first-child').classList.add('active');
                document.getElementById('manual-tab').classList.add('active');
            } else {
                document.querySelector('.tab-button:last-child').classList.add('active');
                document.getElementById('csv-tab').classList.add('active');
            }
        }

        function loadSettings() {
            const saved = localStorage.getItem('uploader_config');
            if (saved) {
                config = JSON.parse(saved);
                // Populate all fields including Google API
                document.getElementById('site-url').value = config.siteUrl || '';
                document.getElementById('consumer-key').value = config.consumerKey || '';
                document.getElementById('consumer-secret').value = config.consumerSecret || '';
                document.getElementById('anthropic-key').value = config.anthropicKey || '';
                document.getElementById('google-api-key').value = config.googleApiKey || '';
                document.getElementById('google-search-id').value = config.googleSearchId || '';
                
                // Only hide setup if we have Google API credentials
                if (config.googleApiKey && config.googleSearchId) {
                    document.getElementById('setup-overlay').classList.add('hidden');
                } else {
                    // Show setup to add missing Google credentials
                    document.getElementById('setup-overlay').classList.remove('hidden');
                }
            }
        }

        function openSettings() {
            document.getElementById('setup-overlay').classList.remove('hidden');
        }

        function saveSettings() {
            const siteUrl = document.getElementById('site-url').value.trim();
            const consumerKey = document.getElementById('consumer-key').value.trim();
            const consumerSecret = document.getElementById('consumer-secret').value.trim();
            const anthropicKey = document.getElementById('anthropic-key').value.trim();
            const googleApiKey = document.getElementById('google-api-key').value.trim();
            const googleSearchId = document.getElementById('google-search-id').value.trim();

            if (!siteUrl || !consumerKey || !consumerSecret || !anthropicKey || !googleApiKey || !googleSearchId) {
                alert('אנא מלא את כל השדות');
                return;
            }

            config = { siteUrl, consumerKey, consumerSecret, anthropicKey, googleApiKey, googleSearchId };
            localStorage.setItem('uploader_config', JSON.stringify(config));
            document.getElementById('setup-overlay').classList.add('hidden');
            showAlert('manual', '✅ ההגדרות נשמרו בהצלחה!', 'success');
        }

        function showAlert(tab, message, type) {
            const alertDiv = document.getElementById(`${tab}-alert`);
            alertDiv.className = `alert alert-${type}`;
            alertDiv.innerHTML = message;
            alertDiv.style.display = 'flex';
            
            setTimeout(() => {
                alertDiv.style.display = 'none';
            }, 5000);
        }

        // Character counter
        document.addEventListener('DOMContentLoaded', function() {
            const metaDesc = document.getElementById('meta-description');
            if (metaDesc) {
                metaDesc.addEventListener('input', function(e) {
                    const length = e.target.value.length;
                    const counter = document.getElementById('char-counter');
                    counter.textContent = `${length}/150 תווים`;
                    
                    if (length > 145) counter.className = 'char-counter warning';
                    else if (length === 150) counter.className = 'char-counter error';
                    else counter.className = 'char-counter';
                });
            }
        });

        async function generateContent() {
            const productName = document.getElementById('product-name').value.trim();
            const price = document.getElementById('product-price').value.trim();
            const categories = getSelectedCategories();
            const keywords = document.getElementById('product-keywords').value.trim();
            const israeliProduct = document.getElementById('israeli-product').checked;

            if (!productName || !price || !categories || !keywords) {
                showAlert('manual', '❌ אנא מלא את כל השדות ובחר לפחות קטגוריה אחת', 'error');
                return;
            }

            if (!config) {
                showAlert('manual', '❌ אנא הגדר את המערכת תחילה', 'error');
                document.getElementById('setup-overlay').classList.remove('hidden');
                return;
            }

            const btn = document.getElementById('generate-btn');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> <span>מייצר תוכן עם AI...</span>';

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product_name: productName,
                        keywords: keywords,
                        anthropic_key: config.anthropicKey,
                        google_api_key: config.googleApiKey,
                        google_search_id: config.googleSearchId,
                        israeli_product: israeliProduct
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'שגיאה ביצירת התוכן');
                }

                document.getElementById('product-description').value = data.description;
                document.getElementById('seo-title').value = data.seo_title;
                document.getElementById('meta-description').value = data.meta_description;
                document.getElementById('focus-keyphrase').value = keywords;
                document.getElementById('char-counter').textContent = `${data.meta_description.length}/150 תווים`;

                // Store all alternative images
                alternativeImages = data.alternative_images || [];
                currentImageIndex = 0;
                
                if (alternativeImages.length > 0) {
                    currentImageUrl = alternativeImages[0].preview_url;
                    originalImageUrl = alternativeImages[0].original_url;
                } else {
                    currentImageUrl = data.image_url;
                    originalImageUrl = data.original_image_url || null;
                }
                
                console.log(`Loaded ${alternativeImages.length} alternative images`);
                console.log('Current original URL:', originalImageUrl);
                
                const previewDiv = document.getElementById('preview-image');
                previewDiv.classList.remove('empty');
                previewDiv.innerHTML = `
                    <img src="${currentImageUrl}" 
                         alt="${productName}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain;"
                         onerror="this.style.display='none'; this.parentElement.innerHTML='<div style=\\'text-align:center; padding:2rem;\\'><div style=\\'font-size:4rem;\\'>📸</div><div style=\\'color:var(--text-light);\\'>תמונה זמנית</div></div>'">
                `;
                
                // Show/hide change image button
                const changeImageContainer = document.getElementById('change-image-container');
                const imageCounter = document.getElementById('image-counter');
                if (alternativeImages.length > 1) {
                    changeImageContainer.style.display = 'block';
                    imageCounter.textContent = `1/${alternativeImages.length}`;
                } else {
                    changeImageContainer.style.display = 'none';
                }

                document.getElementById('preview-section').classList.remove('hidden');
                showAlert('manual', '✅ התוכן נוצר בהצלחה עם AI!', 'success');
            } catch (error) {
                showAlert('manual', `❌ שגיאה: ${error.message}`, 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<span>🤖 יצירת תוכן עם AI</span>';
            }
        }

        async function uploadProduct() {
            if (!config) {
                showAlert('manual', '❌ אנא הגדר את המערכת תחילה', 'error');
                return;
            }

            const btn = document.getElementById('upload-btn');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> <span>מעלה...</span>';

            try {
                const productData = {
                    name: document.getElementById('product-name').value.trim(),
                    price: document.getElementById('product-price').value.trim(),
                    category: getSelectedCategories(),
                    description: document.getElementById('product-description').value.trim(),
                    seo_title: document.getElementById('seo-title').value.trim(),
                    meta_description: document.getElementById('meta-description').value.trim(),
                    focus_keyphrase: document.getElementById('focus-keyphrase').value.trim(),
                    image_url: currentImageUrl,
                    original_image_url: originalImageUrl,
                    woo_config: {
                        site_url: config.siteUrl,
                        consumer_key: config.consumerKey,
                        consumer_secret: config.consumerSecret
                    }
                };

                console.log('Sending productData with original_image_url:', originalImageUrl);

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(productData)
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'שגיאה בהעלאה');
                }

                showAlert('manual', `✅ המוצר "${data.name}" הועלה בהצלחה!`, 'success');
                setTimeout(clearForm, 2000);
            } catch (error) {
                showAlert('manual', `❌ שגיאה: ${error.message}`, 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '📤 העלה למחסן WooCommerce';
            }
        }

        function changeImage() {
            if (alternativeImages.length <= 1) return;
            
            // Cycle to next image
            currentImageIndex = (currentImageIndex + 1) % alternativeImages.length;
            
            // Update current URLs
            const imageData = alternativeImages[currentImageIndex];
            currentImageUrl = imageData.preview_url;
            originalImageUrl = imageData.original_url;
            
            // Update preview
            const previewDiv = document.getElementById('preview-image');
            const productName = document.getElementById('product-name').value.trim();
            previewDiv.innerHTML = `
                <img src="${currentImageUrl}" 
                     alt="${productName}" 
                     style="max-width: 100%; max-height: 100%; object-fit: contain;"
                     onerror="this.style.display='none'; this.parentElement.innerHTML='<div style=\\'text-align:center; padding:2rem;\\'><div style=\\'font-size:4rem;\\'>📸</div><div style=\\'color:var(--text-light);\\'>תמונה זמנית</div></div>'">
            `;
            
            // Update counter
            document.getElementById('image-counter').textContent = `${currentImageIndex + 1}/${alternativeImages.length}`;
            
            console.log(`Changed to image ${currentImageIndex + 1}/${alternativeImages.length}`);
            console.log('New original URL:', originalImageUrl);
        }

        function clearForm() {
            document.getElementById('product-name').value = '';
            document.getElementById('product-price').value = '';
            // Uncheck all categories
            document.querySelectorAll('#category-tree input[name="categories"]').forEach(cb => cb.checked = false);
            document.getElementById('product-keywords').value = '';
            document.getElementById('product-description').value = '';
            document.getElementById('seo-title').value = '';
            document.getElementById('meta-description').value = '';
            document.getElementById('focus-keyphrase').value = '';
            document.getElementById('char-counter').textContent = '0/150 תווים';
            document.getElementById('preview-section').classList.add('hidden');
            
            const previewDiv = document.getElementById('preview-image');
            previewDiv.classList.add('empty');
            previewDiv.innerHTML = 'תמונה תופיע כאן לאחר היצירה';
            
            // Reset image data
            currentImageUrl = null;
            originalImageUrl = null;
            alternativeImages = [];
            currentImageIndex = 0;
            document.getElementById('change-image-container').style.display = 'none';
        }

        function handleCSVUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                const text = e.target.result;
                parseCSV(text);
            };
            reader.readAsText(file);
        }

        function parseCSV(text) {
            const lines = text.split('\\n').filter(line => line.trim());
            if (lines.length < 2) {
                showAlert('csv', '❌ הקובץ ריק או לא תקין', 'error');
                return;
            }

            csvData = [];
            for (let i = 1; i < lines.length; i++) {
                const parts = lines[i].split(',');
                if (parts.length >= 4) {
                    csvData.push({
                        name: parts[0].trim(),
                        price: parts[1].trim(),
                        category: parts[2].trim(),
                        keywords: parts[3].trim()
                    });
                }
            }

            if (csvData.length === 0) {
                showAlert('csv', '❌ לא נמצאו מוצרים תקינים בקובץ', 'error');
                return;
            }

            document.getElementById('csv-processing').classList.remove('hidden');
            document.getElementById('csv-total').textContent = csvData.length;
            showAlert('csv', `✅ נטענו ${csvData.length} מוצרים`, 'success');
        }

        async function processCSV() {
            if (!config) {
                showAlert('csv', '❌ אנא הגדר את המערכת תחילה', 'error');
                document.getElementById('setup-overlay').classList.remove('hidden');
                return;
            }

            const btn = document.getElementById('csv-process-btn');
            btn.disabled = true;

            document.getElementById('csv-current-product').style.display = 'block';

            let completed = 0;
            let failed = 0;

            for (let i = 0; i < csvData.length; i++) {
                const product = csvData[i];
                document.getElementById('csv-current-text').textContent = `מעבד מוצר ${i + 1}/${csvData.length}: ${product.name}`;

                try {
                    const response = await fetch('/api/process-product', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            product: product,
                            config: config
                        })
                    });

                    if (response.ok) {
                        completed++;
                    } else {
                        failed++;
                    }
                } catch (error) {
                    failed++;
                }

                document.getElementById('csv-completed').textContent = completed;
                document.getElementById('csv-failed').textContent = failed;
                
                const progress = ((i + 1) / csvData.length) * 100;
                document.getElementById('csv-progress').style.width = `${progress}%`;
            }

            document.getElementById('csv-current-text').textContent = `✅ הסתיים! ${completed} מוצרים הועלו, ${failed} נכשלו`;
            btn.disabled = false;
        }

        function resetCSV() {
            csvData = [];
            document.getElementById('csv-processing').classList.add('hidden');
            document.getElementById('csv-file').value = '';
            document.getElementById('csv-total').textContent = '0';
            document.getElementById('csv-completed').textContent = '0';
            document.getElementById('csv-failed').textContent = '0';
            document.getElementById('csv-progress').style.width = '0%';
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/temp_images/<filename>')
def serve_temp_image(filename):
    """Serve temporary images for WooCommerce to fetch"""
    return send_from_directory(TEMP_IMAGES_DIR, filename)


@app.route('/api/generate', methods=['POST'])
def generate_content():
    """Generate AI content for product"""
    try:
        data = request.json
        product_name = data.get('product_name')
        keywords = data.get('keywords')
        anthropic_key = data.get('anthropic_key')
        google_api_key = data.get('google_api_key')
        google_search_id = data.get('google_search_id')
        israeli_product = data.get('israeli_product', False)  # Get Israeli product flag

        if not all([product_name, keywords, anthropic_key, google_api_key, google_search_id]):
            return jsonify({'error': 'חסרים נתונים - אנא מלא את כל השדות'}), 400

        # Validate API key format
        if not anthropic_key.startswith('sk-ant-'):
            return jsonify({'error': 'מפתח Claude API לא תקין. המפתח צריך להתחיל ב-sk-ant-'}), 400

        try:
            # Generate SEO description
            description = generate_seo_description(product_name, keywords, anthropic_key)
            
            # Generate SEO title
            seo_title = generate_seo_title(product_name, keywords, anthropic_key)
            
            # Generate meta description
            meta_description = generate_meta_description(product_name, keywords, description, anthropic_key)
            
            # Step 1: Translate product name to English (or keep Hebrew for Israeli products)
            print(f"🌐 Translating product name: {product_name}")
            try:
                if israeli_product:
                    translation_prompt = f"""You are a cycling expert. The following is a bike product name in Hebrew.
Translate it to a clean, accurate Hebrew search term suitable for Israeli bike retail sites.
Keep brand names and model numbers exactly as written. Keep Hebrew product type words.
Output only the search term, nothing else.

Product: {product_name}"""
                else:
                    translation_prompt = f"""You are a cycling expert. The following is a bike product name, possibly in Hebrew or mixed Hebrew/English.
Translate it to accurate English, preserving brand names, model numbers, and all numeric specs (sizes, speeds, tooth ranges, etc.) exactly as they appear.
Do NOT add, remove, or modify any numbers, letters, suffixes, or specs — translate only the Hebrew words.
Output only the English translation, nothing else.

Product: {product_name}"""

                english_name = call_claude_api(translation_prompt, anthropic_key).strip()
                print(f"✅ Translated: {english_name}")
            except Exception as e:
                print(f"⚠️ Translation failed: {e}, using original name")
                english_name = product_name

            product_specs = {
                'brand': '',
                'size': '',
                'type': '',
                'search_term': english_name
            }
            
            # Fetch real product images from bike retailers (up to 10)
            print(f"🔍 Searching bike retailers for: {product_name}")
            print(f"🇮🇱 Israeli product flag: {israeli_product}")
            all_images = fetch_product_image_from_retailers(
                product_name=product_specs.get('search_term', product_name),
                product_specs=product_specs,
                google_api_key=google_api_key,
                google_search_id=google_search_id,
                max_images=10,
                israeli_product=israeli_product
            )
            
            if not all_images:
                return jsonify({'error': 'לא נמצאה תמונה מתאימה'}), 404
            
            # Process all images: create base64 for preview
            image_data_list = []
            for idx, (image_bytes, image_type, original_url) in enumerate(all_images):
                # Create base64 for preview
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                preview_url = f"data:image/jpeg;base64,{image_base64}"
                
                image_data_list.append({
                    'preview_url': preview_url,
                    'original_url': original_url,
                    'index': idx
                })
            
            # Return first image as main, all as alternatives
            return jsonify({
                'description': description,
                'seo_title': seo_title,
                'meta_description': meta_description,
                'image_url': image_data_list[0]['preview_url'],
                'original_image_url': image_data_list[0]['original_url'],
                'alternative_images': image_data_list
            })
        
        except Exception as api_error:
            error_msg = str(api_error)
            if "401" in error_msg or "authentication" in error_msg.lower():
                return jsonify({'error': 'מפתח Claude API לא תקין. אנא בדוק את המפתח ונסה שוב'}), 401
            elif "429" in error_msg:
                return jsonify({'error': 'עברת את מכסת הבקשות. נסה שוב בעוד כמה דקות'}), 429
            elif "overloaded" in error_msg.lower():
                return jsonify({'error': 'שרתי Claude עמוסים כרגע. נסה שוב בעוד רגע'}), 503
            else:
                return jsonify({'error': f'שגיאה ביצירת תוכן: {error_msg}'}), 500

    except Exception as e:
        return jsonify({'error': f'שגיאה כללית: {str(e)}'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_product():
    """Upload product to WooCommerce"""
    try:
        data = request.json
        woo_config = data.get('woo_config')
        
        auth = base64.b64encode(f"{woo_config['consumer_key']}:{woo_config['consumer_secret']}".encode()).decode()
        
        # Parse categories from comma-separated string
        category_string = data.get('category', '')
        category_names = [cat.strip() for cat in category_string.split(',') if cat.strip()]
        
        # Get or create category IDs
        category_ids = []
        if category_names:
            # Fetch existing categories from WooCommerce
            cat_response = requests.get(
                f"{woo_config['site_url']}/wp-json/wc/v3/products/categories",
                headers={'Authorization': f'Basic {auth}'},
                params={'per_page': 100}
            )
            
            if cat_response.status_code == 200:
                existing_categories = {cat['name']: cat['id'] for cat in cat_response.json()}
                print(f"Found {len(existing_categories)} existing categories")
                
                # Match or create categories
                for cat_name in category_names:
                    if cat_name in existing_categories:
                        category_ids.append({'id': existing_categories[cat_name]})
                        print(f"✅ Using existing category: {cat_name} (ID: {existing_categories[cat_name]})")
                    else:
                        # Create new category
                        new_cat_response = requests.post(
                            f"{woo_config['site_url']}/wp-json/wc/v3/products/categories",
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': f'Basic {auth}'
                            },
                            json={'name': cat_name}
                        )
                        if new_cat_response.status_code in [200, 201]:
                            new_cat_id = new_cat_response.json()['id']
                            category_ids.append({'id': new_cat_id})
                            print(f"✅ Created new category: {cat_name} (ID: {new_cat_id})")
                        else:
                            print(f"⚠️ Failed to create category: {cat_name}")
            else:
                print(f"⚠️ Failed to fetch categories: {cat_response.status_code}")
        
        product_data = {
            'name': data.get('name'),
            'regular_price': data.get('price'),
            'description': data.get('description'),
            'categories': category_ids,
            'meta_data': [
                {'key': '_yoast_wpseo_title', 'value': data.get('seo_title')},
                {'key': '_yoast_wpseo_metadesc', 'value': data.get('meta_description')},
                {'key': '_yoast_wpseo_focuskw', 'value': data.get('focus_keyphrase')}
            ]
        }
        
        print(f"Product categories: {category_ids}")

        # Upload to WooCommerce first without image
        response = requests.post(
            f"{woo_config['site_url']}/wp-json/wc/v3/products",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth}'
            },
            json=product_data
        )

        if response.status_code not in [200, 201]:
            error_detail = response.text
            print(f"WooCommerce API Error {response.status_code}: {error_detail}")
            print(f"Product data sent: {product_data}")
            return jsonify({'error': f'WooCommerce error: {response.status_code} - {error_detail}'}), 400

        result = response.json()
        product_id = result.get('id')
        print(f"✅ Product created successfully: {result.get('name')} (ID: {product_id})")
        print(f"Categories assigned: {result.get('categories', [])}")
        
        # Now try to add image to the created product using WordPress REST API
        original_image_url = data.get('original_image_url')
        print(f"DEBUG: original_image_url from request: {original_image_url}")
        print(f"DEBUG: All data keys: {list(data.keys())}")
        
        if original_image_url and product_id:
            try:
                print(f"Attempting to add image to product {product_id}...")
                print(f"Downloading image from: {original_image_url[:100]}...")
                
                # Download the image from the retailer
                img_response = requests.get(original_image_url, timeout=10)
                if img_response.status_code == 200:
                    print(f"✅ Downloaded image: {len(img_response.content)} bytes")
                    
                    # WordPress Application Password credentials (hardcoded for now - move to config later)
                    WP_USERNAME = "image-uploader"
                    WP_APP_PASSWORD = "ajXjCAE8is5rgU4xsflaWvSP"  # Remove spaces
                    
                    # Detect MIME type
                    content_type = img_response.headers.get('content-type', 'image/jpeg')
                    
                    # Extract filename from URL or generate one
                    filename = original_image_url.split('/')[-1].split('?')[0]
                    if not filename or '.' not in filename:
                        ext = '.jpg' if 'jpeg' in content_type else '.png' if 'png' in content_type else '.jpg'
                        filename = f"product-image-{product_id}{ext}"
                    
                    print(f"Uploading to WordPress Media Library as: {filename}")
                    
                    # Upload to WordPress REST API /wp/v2/media
                    files = {
                        'file': (filename, img_response.content, content_type)
                    }
                    
                    upload_data = {
                        'title': f"Product {product_id} Image",
                        'alt_text': data.get('name', 'Product image'),
                        'caption': f"Image for product {product_id}"
                    }
                    
                    media_response = requests.post(
                        f"{woo_config['site_url']}/wp-json/wp/v2/media",
                        auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
                        files=files,
                        data=upload_data,
                        timeout=30
                    )
                    
                    if media_response.status_code == 201:
                        media_data = media_response.json()
                        media_id = media_data.get('id')
                        media_url = media_data.get('source_url')
                        print(f"✅ Image uploaded to WordPress: ID={media_id}, URL={media_url}")
                        
                        # Now attach the image to the product
                        print(f"Attaching image to product {product_id}...")
                        update_response = requests.put(
                            f"{woo_config['site_url']}/wp-json/wc/v3/products/{product_id}",
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': f'Basic {auth}'
                            },
                            json={'images': [{'id': media_id}]}
                        )
                        
                        if update_response.status_code in [200, 201]:
                            print(f"✅ Image attached to product successfully!")
                        else:
                            print(f"⚠️ Failed to attach image to product: {update_response.status_code}")
                            print(f"Response: {update_response.text[:300]}")
                    else:
                        print(f"⚠️ Failed to upload image to WordPress: {media_response.status_code}")
                        print(f"Response: {media_response.text[:500]}")
                        print("Product created without image")
                else:
                    print(f"⚠️ Failed to download image: {img_response.status_code}")
                    print("Product created without image")
                    
            except Exception as img_error:
                print(f"⚠️ Error uploading image: {img_error}")
                import traceback
                traceback.print_exc()
                print("Product created without image")
        else:
            print(f"⚠️ No original_image_url provided (original_image_url={original_image_url}, product_id={product_id})")

        return jsonify({'success': True, 'name': result.get('name'), 'id': result.get('id')})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process-product', methods=['POST'])
def process_product():
    """Process and upload a single product from CSV"""
    try:
        data = request.json
        product = data.get('product')
        config = data.get('config')

        # Generate content
        description = generate_seo_description(product['name'], product['keywords'], config['anthropicKey'])
        seo_title = generate_seo_title(product['name'], product['keywords'], config['anthropicKey'])
        meta_description = generate_meta_description(product['name'], product['keywords'], description, config['anthropicKey'])

        # Upload to WooCommerce
        product_data = {
            'name': product['name'],
            'regular_price': product['price'],
            'description': description,
            'categories': [{'name': product['category']}],
            'meta_data': [
                {'key': '_yoast_wpseo_title', 'value': seo_title},
                {'key': '_yoast_wpseo_metadesc', 'value': meta_description},
                {'key': '_yoast_wpseo_focuskw', 'value': product['keywords']}
            ]
        }

        auth = base64.b64encode(f"{config['consumerKey']}:{config['consumerSecret']}".encode()).decode()
        
        response = requests.post(
            f"{config['siteUrl']}/wp-json/wc/v3/products",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth}'
            },
            json=product_data
        )

        if response.status_code not in [200, 201]:
            return jsonify({'error': 'Upload failed'}), 400

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def call_claude_api(prompt: str, api_key: str) -> str:
    """Call Claude API"""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 4096,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=60
        )
        
        if response.status_code != 200:
            error_detail = response.text
            raise Exception(f"Claude API error {response.status_code}: {error_detail}")
        
        data = response.json()
        return data['content'][0]['text']
    except requests.exceptions.RequestException as e:
        raise Exception(f"שגיאה בחיבור ל-Claude API: {str(e)}")
    except KeyError as e:
        raise Exception(f"פורמט תשובה לא תקין מ-Claude API: {str(e)}")
    except Exception as e:
        raise Exception(f"שגיאה: {str(e)}")


def convert_to_wordpress_blocks(text):
    """
    Convert plain text to WordPress Gutenberg blocks format
    
    This creates proper headings (H2, H3) instead of everything being wrapped in <p> tags
    
    Detection rules:
    - Lines ending with emoji 🚴 🎯 ⭐ = H2 (main heading)
    - Lines ending with ? = H3 (question heading)
    - Short lines (<60 chars) followed by long text = H3 (section title)
    - Lines starting with ✔ = List items
    - Lines with | (pipe) = Italic footer text
    - Lines with 🛒 = Bold CTA paragraph
    - Everything else = Regular paragraph
    """
    lines = text.split('\n')
    blocks = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Rule 1: Line with emoji at the end (except 🛒) = H2 (main heading)
        if any(emoji in line for emoji in ['🚴', '🎯', '⭐', '💎', '🏆', '✨']):
            blocks.append(f'''<!-- wp:heading {{"level":2}} -->
<h2 class="wp-block-heading">{line}</h2>
<!-- /wp:heading -->''')
            i += 1
            continue
        
        # Rule 2: Lines ending with ? = H3 (question heading)
        if line.endswith('?'):
            blocks.append(f'''<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">{line}</h3>
<!-- /wp:heading -->''')
            i += 1
            continue
        
        # Rule 3: Short lines (< 60 chars) that look like titles = H3
        # Check if next line is longer (indicates this is a title)
        if len(line) < 60 and not line.startswith('✔') and not '|' in line:
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # If next line is significantly longer or empty (spacing), this is likely a title
                if len(next_line) > 60 or not next_line:
                    blocks.append(f'''<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">{line}</h3>
<!-- /wp:heading -->''')
                    i += 1
                    continue
        
        # Rule 4: Collect consecutive ✔ lines into a list
        if line.startswith('✔'):
            list_items = []
            while i < len(lines) and lines[i].strip().startswith('✔'):
                list_items.append(lines[i].strip())
                i += 1
            
            # Create list block
            list_html = '\n'.join([f'<li>{item}</li>' for item in list_items])
            blocks.append(f'''<!-- wp:list -->
<ul class="wp-block-list">
{list_html}
</ul>
<!-- /wp:list -->''')
            continue
        
        # Rule 5: Lines with 🛒 = bold CTA paragraph
        if '🛒' in line:
            blocks.append(f'''<!-- wp:paragraph -->
<p><strong>{line}</strong></p>
<!-- /wp:paragraph -->''')
            i += 1
            continue
        
        # Rule 6: Lines with | (pipe) are special formatting (footer)
        if '|' in line:
            blocks.append(f'''<!-- wp:paragraph -->
<p><em>{line}</em></p>
<!-- /wp:paragraph -->''')
            i += 1
            continue
        
        # Rule 7: Everything else = paragraph
        blocks.append(f'''<!-- wp:paragraph -->
<p>{line}</p>
<!-- /wp:paragraph -->''')
        i += 1
    
    return '\n\n'.join(blocks)


def generate_seo_description(product_name: str, keywords: str, api_key: str) -> str:
    """Generate comprehensive SEO-optimized product description using Claude"""
    # Extract focus keyphrase from keywords (take first 3-4 keywords)
    keyword_list = [k.strip() for k in keywords.split('|') if k.strip()]
    focus_keyphrase = ' '.join(keyword_list[:4])  # Take first 4 keywords for focus keyphrase
    
    prompt = f"""אתה כותב תוכן מקצועי ומומחה SEO לאתרי מכירות מוצרי אופניים. תפקידך לכתוב תיאור מוצר ארוך, עשיר ומפורט שיקדם את המוצר בגוגל ויעודד לקוחות לקנות.

שם המוצר: {product_name}
מילות מפתח: {keywords}
ביטוי מפתח מרכזי (Focus Keyphrase): {focus_keyphrase}

כתוב תיאור מוצר מלא ומקיף בעברית. עקוב אחרי המבנה הבא, אבל כתוב תוכן אמיתי ומקורי - לא סוגריים מרובעים!

**חשוב מאוד: אל תכתוב סוגריים מרובעים [...] בתשובה! כתוב את התוכן עצמו!**

המבנה הנדרש:

כותרת ראשית עם שם המוצר המלא ותיאור קצר 🚴

פסקת פתיחה של 3-4 משפטים המסבירה מה המוצר, למי הוא מתאים ומה היתרונות העיקריים. שלב את "{focus_keyphrase}" באופן טבעי.

שם המוצר המלא – תיאור הפתרון שהוא מספק

פסקה של 3-4 משפטים המרחיבה על המוצר והיתרונות שלו. שלב את "{focus_keyphrase}" באופן טבעי.

למה לבחור ב{product_name}?

כותרת על תכונה מרכזית של המוצר

פסקה של 3-4 משפטים המסבירה את התכונה החשובה הזו. שלב שוב את "{focus_keyphrase}".

כותרת על איכות או טכנולוגיה

פסקה של 3-4 משפטים על איכות המוצר, בדיקות, תקנים או טכנולוגיה. הזכר מותגים באנגלית אם רלוונטי.

מפרט טכני – {product_name}

פסקה אחת ארוכה המפרטת את כל הפרטים הטכניים בצורה רצופה וקריאה, ללא רשימה. למשל: "המוצר מתאים לגילאי X-Y, משקל עד Z ק"ג, כולל את מערכת ABC, משקל המוצר W ק"ג, ונבדק על פי תקן XYZ." שלב את "{focus_keyphrase}" גם כאן.

יתרונות נוספים של {focus_keyphrase}

✔ יתרון ראשון – הסבר מפורט במשפט מלא
✔ יתרון שני – הסבר מפורט במשפט מלא  
✔ יתרון שלישי – הסבר מפורט במשפט מלא
✔ יתרון רביעי – הסבר מפורט במשפט מלא
✔ יתרון חמישי – הסבר מפורט במשפט מלא

למי מתאים {product_name}?

פסקה של 3-4 משפטים המתארת את קהל היעד, מתי כדאי להשתמש במוצר, ואילו צרכים הוא פותר. שלב את "{focus_keyphrase}" פעם נוספת.

סיכום – למה {focus_keyphrase} הוא הבחירה הנכונה?

פסקת סיכום של 4-5 משפטים המסכמת את כל היתרונות, מדגישה את הערך של המוצר, ומעודדת רכישה. השתמש ב-"{focus_keyphrase}" פעם אחרונה.

🛒 הזמינו עכשיו את {product_name} ותתחילו ליהנות מהיתרונות!

משלוח מהיר לכל הארץ | אחריות יבואן רשמי | שירות לקוחות מקצועי

דרישות חובה:
1. אורך כולל: לפחות 400 מילים (לא תווים!)
2. הביטוי "{focus_keyphrase}" חייב להופיע לפחות 5-7 פעמים באופן טבעי
3. אל תשתמש בסימני Markdown (#, ##, **)
4. אל תשתמש בסוגריים מרובעים [...] - כתוב את התוכן המלא!
5. השתמש בשורות ריקות להפרדה בין סעיפים
6. כלול רשימת יתרונות עם ✔
7. כתוב בעברית מקצועית וקולחת
8. התחל ישירות עם הכותרת הראשית
9. סיים עם קריאה לפעולה ושורת משלוח/אחריות
10. השתמש באימוג'י 🚴 בכותרת הראשית ו-🛒 לפני הקריאה לפעולה

חשוב ביותר: 
- זה תיאור ארוך ומקיף של 400+ מילים!
- כתוב תוכן אמיתי ומלא - לא סוגריים או placeholders
- אל תכתוב [...] או [שם המוצר] - כתוב את שם המוצר בפועל
- כל המשפטים צריכים להיות מלאים ואמיתיים"""

    # Generate plain text description
    plain_text = call_claude_api(prompt, api_key).strip()
    
    # Convert to WordPress Gutenberg blocks format for proper heading rendering
    wordpress_blocks = convert_to_wordpress_blocks(plain_text)
    
    return wordpress_blocks


def generate_seo_title(product_name: str, keywords: str, api_key: str) -> str:
    """Generate SEO title using Claude"""
    prompt = f"""צור כותרת SEO אופטימלית בעברית למוצר זה:

שם המוצר: {product_name}
מילות מפתח: {keywords}

הכותרת צריכה:
- להיות בעברית (עם שמות מותגים באנגלית אם יש)
- להיות 50-60 תווים
- לכלול מילת מפתח מרכזית
- להיות בפורמט: "תיאור בעברית Brand" (לדוגמה: "שמן שרשרת אופניים Squirt")

השב רק עם הכותרת, ללא הסברים."""

    return call_claude_api(prompt, api_key).strip()


def generate_meta_description(product_name: str, keywords: str, description: str, api_key: str) -> str:
    """Generate meta description using Claude"""
    prompt = f"""צור Meta Description בעברית למוצר זה:

שם המוצר: {product_name}
מילות מפתח: {keywords}
תיאור מלא: {description}

Meta Description חייב:
- להיות בדיוק 150 תווים או פחות (כולל רווחים)
- בעברית בלבד
- מושך ואינפורמטיבי
- כולל קריאה לפעולה

השב רק עם ה-Meta Description, ללא הסברים או תווים נוספים."""

    result = call_claude_api(prompt, api_key).strip()
    return result[:150]  # Ensure max 150 chars


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚴  MyBikeStore Product Uploader")
    print("="*50)
    print("\n✅ The Server is Running!")
    print("🌐 Open The Browser and Go To:")
    print("   http://localhost:5001")
    print("\n💡 To Stop Press: Ctrl+C")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)