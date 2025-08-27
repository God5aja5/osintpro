from flask import request, session, jsonify, render_template_string
from models import db
from flask import redirect, url_for
from flask import redirect, url_for
from utils import login_required, admin_required, check_credits, update_user_activity, is_user_online, cost_banner
from templates import get_base_template
import uuid
import time
from config import *
import random
import base64
from io import BytesIO
from datetime import datetime
import json
import random
import string

# Import configuration variables
from config import CONFIG

# Enhanced Info Pages with Mobile UI Fixes + Sound + Maintenance awareness
def register_routes(app):
    @app.route('/vehicle-info')
    @login_required
    def vehicle_info():
        if not check_credits(session['username']):
            return redirect(url_for('pricing'))
        
        content = (
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div class="search-container">'
            '<h2 style="color: var(--primary-red); text-align: center; margin-bottom: 10px;"><i class="fas fa-car"></i> Vehicle Information Search</h2>'
            + cost_banner() +
            '<form class="search-form" onsubmit="searchVehicle(event)"><input type="text" class="search-input" id="vehicleNumber" placeholder="Enter vehicle number (e.g., MH01AB1234)" required><button type="submit" class="search-btn">Search</button></form>'
            '</div><div id="results"></div>'
            '<script>'
            'async function searchVehicle(e){ e.preventDefault(); playSound("click"); const vehicleNumber=document.getElementById("vehicleNumber").value.toUpperCase(); const resultsDiv=document.getElementById("results"); resultsDiv.innerHTML = \'<div class="loading"><div class="loading-spinner"></div><p>Searching vehicle database...</p></div>\';'
            'try{ const response=await fetch("/api/vehicle/"+vehicleNumber); const data=await response.json();'
            ' if(response.status===503 && data && data.message){ resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(234,179,8,0.1); border-radius: 10px; color: var(--warning-yellow);"><i class="fas fa-wrench"></i> \' + escapeHtml(data.message) + \'</div>\'; playSound("error"); return; }'
            ' if(response.ok && data.d){ const info=filterData(data.d); let html=\'<div class="results-container"><h3 style="margin-bottom:20px;">Vehicle Details</h3>\';'
            ' html+=\'<div class="data-grid">\''
            ' + createDataCard("Registration", info.regNo || info.vehicleNumber || vehicleNumber)'
            ' + createDataCard("Owner", info.owner || "-")'
            ' + createDataCard("Model", info.model || "-")'
            ' + createDataCard("Registration Date", info.regDate || "-")'
            ' + createDataCard("Fuel Type", info.type || "-")'
            ' + createDataCard("Class", info.class || "-")'
            ' + createDataCard("Engine No", info.engine || "-")'
            ' + createDataCard("Chassis No", info.chassis || "-")'
            ' + createDataCard("RTO", info.regAuthority || "-")'
            ' + createDataCard("Status", info.status || "-")'
            ' + createDataCard("Insurance Valid Till", info.vehicleInsuranceUpto || "-")'
            ' + createDataCard("Color", info.vehicleColour || "-")'
            ' + \'</div>\';'
            ' html += \'<div style="margin-top:30px;"><h4 style="color: var(--primary-red); margin-bottom:15px;">Complete Information</h4>\' + renderObject(info) + \'</div></div>\';'
            ' resultsDiv.innerHTML = html; playSound("success"); } else { resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-exclamation-circle"></i> No data found for this vehicle number</div>\'; playSound("error"); }'
            '} catch(err){ resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-times-circle"></i> Error occurred while searching</div>\'; playSound("error"); } }'
            '</script>'
        )
        return get_base_template('Vehicle Search - OSINT Tool', content, False)

    @app.route('/ifsc-info')
    @login_required
    def ifsc_info():
        if not check_credits(session['username']):
            return redirect(url_for('pricing'))
        
        content = (
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div class="search-container">'
            '<h2 style="color: var(--primary-red); text-align: center; margin-bottom: 10px;"><i class="fas fa-university"></i> IFSC Code Lookup</h2>'
            + cost_banner() +
            '<form class="search-form" onsubmit="searchIFSC(event)"><input type="text" class="search-input" id="ifscCode" placeholder="Enter IFSC code (e.g., SBIN0000300)" required><button type="submit" class="search-btn">Search</button></form>'
            '</div><div id="results"></div>'
            '<script>'
            'async function searchIFSC(e){ e.preventDefault(); playSound("click"); const ifsc=document.getElementById("ifscCode").value.toUpperCase(); const resultsDiv=document.getElementById("results"); resultsDiv.innerHTML = \'<div class="loading"><div class="loading-spinner"></div><p>Looking up bank details...</p></div>\';'
            'try{ const response=await fetch("/api/ifsc/"+ifsc); const data=await response.json();'
            ' if(response.status===503 && data && data.message){ resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(234,179,8,0.1); border-radius: 10px; color: var(--warning-yellow);"><i class="fas fa-wrench"></i> \' + escapeHtml(data.message) + \'</div>\'; playSound("error"); return; }'
            ' if(response.ok && data.d){ const info=filterData(data.d); let html=\'<div class="results-container"><h3 style="margin-bottom:20px;">Bank Branch Details</h3>\';'
            ' html+=\'<div class="data-grid">\''
            ' + createDataCard("Bank", info.BANK || "-")'
            ' + createDataCard("Branch", info.BRANCH || "-")'
            ' + createDataCard("IFSC", info.IFSC || ifsc)'
            ' + createDataCard("MICR", info.MICR || "-")'
            ' + createDataCard("City", info.CITY || "-")'
            ' + createDataCard("District", info.DISTRICT || "-")'
            ' + createDataCard("State", info.STATE || "-")'
            ' + createDataCard("Address", info.ADDRESS || "-")'
            ' + createDataCard("Contact", info.CONTACT || "-")'
            ' + createDataCard("SWIFT", info.SWIFT || "-")'
            ' + createDataCard("UPI", info.UPI ? "Available" : "Not Available")'
            ' + createDataCard("RTGS", info.RTGS ? "Available" : "Not Available")'
            ' + \'</div>\';'
            ' html += \'<div style="margin-top:30px;"><h4 style="color: var(--primary-red); margin-bottom:15px;">All Details</h4>\' + renderObject(info) + \'</div></div>\';'
            ' resultsDiv.innerHTML = html; playSound("success"); } else { resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-exclamation-circle"></i> Invalid IFSC code</div>\'; playSound("error"); }'
            '} catch(err){ resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-times-circle"></i> Error occurred while searching</div>\'; playSound("error"); } }'
            '</script>'
        )
        return get_base_template('IFSC Lookup - OSINT Tool', content, False)

    @app.route('/pincode-info')
    @login_required
    def pincode_info():
        if not check_credits(session['username']):
            return redirect(url_for('pricing'))
        
        content = (
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div class="search-container">'
            '<h2 style="color: var(--primary-red); text-align: center; margin-bottom: 10px;"><i class="fas fa-map-marker-alt"></i> PIN Code Information</h2>'
            + cost_banner() +
            '<form class="search-form" onsubmit="searchPincode(event)"><input type="text" class="search-input" id="pincode" placeholder="Enter PIN code (e.g., 400001)" pattern="[0-9]{6}" required><button type="submit" class="search-btn">Search</button></form>'
            '</div><div id="results"></div>'
            '<script>'
            'async function searchPincode(e){ e.preventDefault(); playSound("click"); const pincode=document.getElementById("pincode").value; const resultsDiv=document.getElementById("results"); resultsDiv.innerHTML = \'<div class="loading"><div class="loading-spinner"></div><p>Fetching location details...</p></div>\';'
            'try{ const response=await fetch("/api/pincode/"+pincode); const data=await response.json();'
            ' if(response.status===503 && data && data.message){ resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(234,179,8,0.1); border-radius: 10px; color: var(--warning-yellow);"><i class="fas fa-wrench"></i> \' + escapeHtml(data.message) + \'</div>\'; playSound("error"); return; }'
            ' if(response.ok && data.d){ let html = \'<div class="results-container">\';'
            ' if(data.d.PostOffice && data.d.PostOffice.length > 0) {'
            '   html += \'<h3 style="margin-bottom:10px;">Location Details</h3>\';'
            '   html += \'<div style="color: var(--success-green); margin-bottom:20px;">\' + (data.d.Message || "Found " + data.d.PostOffice.length + " results") + \'</div>\';'
            '   data.d.PostOffice.forEach((po, idx) => {'
            '     html += \'<div style="margin: 20px 0; padding: 20px; border:1px solid rgba(220,38,38,0.2); border-radius:12px; background:rgba(10,10,10,0.4);">\';'
            '     html += \'<div style="font-weight:700; color:var(--primary-red); margin-bottom:15px;">Result \' + (idx+1) + \': \' + escapeHtml(po.Name || "Post Office") + \'</div>\';'
            '     html += \'<div class="data-grid">\''
            '     + createDataCard("Name", po.Name || "-")'
            '     + createDataCard("PIN Code", po.Pincode || pincode)'
            '     + createDataCard("Branch Type", po.BranchType || "-")'
            '     + createDataCard("Delivery Status", po.DeliveryStatus || "-")'
            '     + createDataCard("Circle", po.Circle || "-")'
            '     + createDataCard("District", po.District || "-")'
            '     + createDataCard("Division", po.Division || "-")'
            '     + createDataCard("Region", po.Region || "-")'
            '     + createDataCard("Block", po.Block || "-")'
            '     + createDataCard("State", po.State || "-")'
            '     + createDataCard("Country", po.Country || "-")'
            '     + \'</div></div>\';'
            '   });'
            ' } else {'
            '   html += \'<div style="color: var(--warning-yellow);">No detailed post office data found</div>\';'
            ' }'
            ' html += \'</div>\'; resultsDiv.innerHTML = html; playSound("success");'
            ' } else { resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-exclamation-circle"></i> Invalid PIN code or no data found</div>\'; playSound("error"); }'
            '} catch(err){ console.error(err); resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-times-circle"></i> Error occurred while searching</div>\'; playSound("error"); } }'
            '</script>'
        )
        return get_base_template('PIN Code Info - OSINT Tool', content, False)

    @app.route('/ip-info')
    @login_required
    def ip_info():
        if not check_credits(session['username']):
            return redirect(url_for('pricing'))
        
        content = (
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div class="search-container">'
            '<h2 style="color: var(--primary-red); text-align: center; margin-bottom: 10px;"><i class="fas fa-globe"></i> IP Address Information</h2>'
            + cost_banner() +
            '<form class="search-form" onsubmit="searchIP(event)"><input type="text" class="search-input" id="ipAddress" placeholder="Enter IP address (e.g., 8.8.8.8)" required><button type="submit" class="search-btn">Search</button></form>'
            '</div><div id="results"></div>'
            '<script>'
            'async function searchIP(e){ e.preventDefault(); playSound("click"); const ip=document.getElementById("ipAddress").value; const resultsDiv=document.getElementById("results"); resultsDiv.innerHTML = \'<div class="loading"><div class="loading-spinner"></div><p>Looking up IP address...</p></div>\';'
            'try{ const response=await fetch("/api/ip/"+ip); const data=await response.json();'
            ' if(response.status===503 && data && data.message){ resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(234,179,8,0.1); border-radius: 10px; color: var(--warning-yellow);"><i class="fas fa-wrench"></i> \' + escapeHtml(data.message) + \'</div>\'; playSound("error"); return; }'
            ' if(response.ok && data.d){ const info=filterData(data.d); let html=\'<div class="results-container"><h3 style="margin-bottom:20px;">IP Address Details</h3>\';'
            ' html+=\'<div class="data-grid">\''
            ' + createDataCard("IP Address", info.ip || info.query || ip)'
            ' + createDataCard("City", info.city || "-")'
            ' + createDataCard("State/Region", (info.state_prov || info.region || info.regionName || "-"))'
            ' + createDataCard("Country", info.country_name || info.country || "-")'
            ' + createDataCard("Country Code", info.country_code2 || info.countryCode || "-")'
            ' + createDataCard("ISP", info.isp || "-")'
            ' + createDataCard("Organization", (info.organization || info.org || "-"))'
            ' + createDataCard("Latitude", info.latitude || info.lat || "-")'
            ' + createDataCard("Longitude", info.longitude || info.lon || "-")'
            ' + createDataCard("Timezone", (info.time_zone && info.time_zone.name) || info.timezone || "-")'
            ' + createDataCard("Currency", (info.currency && info.currency.code) || "-")'
            ' + createDataCard("Calling Code", info.calling_code || "-")'
            ' + \'</div>\';'
            ' if(info.time_zone) {'
            '   html += \'<div style="margin-top:20px; padding:15px; background:rgba(10,10,10,0.5); border-radius:12px;">\';'
            '   html += \'<h4 style="color:var(--info-blue); margin-bottom:10px;">Timezone Information</h4>\';'
            '   html += \'<div class="data-grid">\''
            '   + createDataCard("Timezone", info.time_zone.name || "-")'
            '   + createDataCard("Current Time", info.time_zone.current_time || "-")'
            '   + createDataCard("Offset", info.time_zone.offset || "-")'
            '   + createDataCard("DST", (info.time_zone.is_dst ? "Active" : "Inactive"))'
            '   + \'</div></div>\';'
            ' }'
            ' html += \'<div style="margin-top:30px;"><h4 style="color: var(--primary-red); margin-bottom:15px;">Complete Information</h4>\' + renderObject(info) + \'</div></div>\';'
            ' resultsDiv.innerHTML = html; playSound("success"); } else { resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-exclamation-circle"></i> Invalid IP address or no data found</div>\'; playSound("error"); }'
            '} catch(err){ resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-times-circle"></i> Error occurred while searching</div>\'; playSound("error"); } }'
            '</script>'
        )
        return get_base_template('IP Information - OSINT Tool', content, False)

    @app.route('/phone-info')
    @login_required
    def phone_info():
        if not check_credits(session['username']):
            return redirect(url_for('pricing'))
        
        content = (
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div class="search-container">'
            '<h2 style="color: var(--primary-red); text-align: center; margin-bottom: 10px;"><i class="fas fa-phone"></i> Phone Number Information</h2>'
            + cost_banner() +
            '<form class="search-form" onsubmit="searchPhone(event)"><input type="text" class="search-input" id="phoneNumber" placeholder="Enter phone number" pattern="[0-9]{10}" required><button type="submit" class="search-btn">Search</button></form>'
            '</div><div id="results"></div>'
            '<script>'
            'async function searchPhone(e){ e.preventDefault(); playSound("click"); const phone=document.getElementById("phoneNumber").value; const resultsDiv=document.getElementById("results"); resultsDiv.innerHTML = \'<div class="loading"><div class="loading-spinner"></div><p>Searching phone records...</p></div>\';'
            'try{ const response=await fetch("/api/phone/"+phone); const data=await response.json();'
            ' if(response.status===503 && data && data.message){ resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(234,179,8,0.1); border-radius: 10px; color: var(--warning-yellow);"><i class="fas fa-wrench"></i> \' + escapeHtml(data.message) + \'</div>\'; playSound("error"); return; }'
            ' if(response.ok && data.d){ let html = \'<div class="results-container"><h3>Phone Information</h3>\';'
            ' if(Array.isArray(data.d) && data.d.length > 0){'
            '   html += \'<div style="color: var(--success-green); margin: 20px 0;">Found \' + data.d.length + \' record(s)</div>\';'
            '   data.d.forEach((result, idx)=>{'
            '     html += \'<div style="margin: 20px 0; padding: 20px; border:1px solid rgba(220,38,38,0.2); border-radius:12px; background:rgba(10,10,10,0.4);">\';'
            '     html += \'<div style="font-weight:700; color:var(--primary-red); margin-bottom:15px;">Record \' + (idx+1) + \'</div>\';'
            '     html += \'<div class="data-grid">\''
            '     + createDataCard("Name", result.name || "-")'
            '     + createDataCard("Mobile", result.mobile || phone)'
            '     + createDataCard("Father Name", result.father_name || "-")'
            '     + createDataCard("Address", result.address || "-")'
            '     + createDataCard("Alt Mobile", result.alt_mobile || "-")'
            '     + createDataCard("Circle", result.circle || "-")'
            '     + createDataCard("Email", result.email || "-")'
            '     + createDataCard("ID Number", result.id_number || "-")'
            '     + \'</div></div>\';'
            '   });'
            ' } else {'
            '   html += \'<div style="color: var(--warning-yellow); margin-top:20px;">No records found for this number</div>\';'
            ' }'
            ' html += \'</div>\'; resultsDiv.innerHTML = html; playSound("success");'
            ' } else { resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-exclamation-circle"></i> No data found for this phone number</div>\'; playSound("error"); }'
            '} catch(err){ console.error(err); resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-times-circle"></i> Error occurred while searching</div>\'; playSound("error"); } }'
            '</script>'
        )
        return get_base_template('Phone Lookup - OSINT Tool', content, False)

    @app.route('/freefire-info')
    @login_required
    def freefire_info():
        if not check_credits(session['username']):
            return redirect(url_for('pricing'))
        
        content = (
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div class="search-container">'
            '<h2 style="color: var(--primary-red); text-align: center; margin-bottom: 10px;"><i class="fas fa-gamepad"></i> Free Fire Player Information</h2>'
            + cost_banner() +
            '<form class="search-form" onsubmit="searchFreeFire(event)"><input type="text" class="search-input" id="playerId" placeholder="Enter Free Fire UID" required><button type="submit" class="search-btn">Search</button></form>'
            '</div><div id="results"></div>'
            '<script>'
            'async function searchFreeFire(e){ e.preventDefault(); playSound("click"); const uid=document.getElementById("playerId").value; const resultsDiv=document.getElementById("results"); resultsDiv.innerHTML = \'<div class="loading"><div class="loading-spinner"></div><p>Fetching player stats...</p></div>\';'
            'try{ const response=await fetch("/api/freefire/"+uid); const data=await response.json();'
            ' if(response.status===503 && data && data.message){ resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(234,179,8,0.1); border-radius: 10px; color: var(--warning-yellow);"><i class="fas fa-wrench"></i> \' + escapeHtml(data.message) + \'</div>\'; playSound("error"); return; }'
            ' if(response.ok && data.d && data.d.basicInfo){ const info=filterData(data.d.basicInfo); const social=filterData(data.d.socialInfo || {}); const clan=filterData(data.d.clanBasicInfo || {});'
            ' const initials=(info.nickname||"FF").toString().trim().slice(0,2).toUpperCase();'
            ' let html=\'<div class="results-container"><h3 style="margin-bottom:20px;">Player Profile</h3>\';'
            ' html+=\'<div style="display:flex; align-items:center; gap:20px; margin-bottom:30px; padding:20px; background:rgba(10,10,10,0.5); border-radius:15px;">\';'
            ' html+=\'<div style="width:80px; height:80px; border-radius:50%; background:linear-gradient(135deg, var(--primary-red), var(--purple-accent)); display:flex; align-items:center; justify-content:center; font-weight:800; color:white; font-size:1.8rem;">\' + escapeHtml(initials) + \'</div>\';'
            ' html+=\'<div style="flex:1;"><div style="font-size:1.5rem; font-weight:700; color:white;">\' + escapeHtml(info.nickname || "Unknown") + \'</div>\';'
            ' html+=\'<div style="color:var(--text-gray); margin-top:5px;">UID: \' + escapeHtml(info.accountId || uid) + \' • Level \' + escapeHtml(info.level || "-") + \' • Region: \' + escapeHtml(info.region || "-") + \'</div></div></div>\';'
            ' html+=\'<div class="data-grid">\''
            ' + createDataCard("Level", info.level || "-")'
            ' + createDataCard("Experience", info.exp || "-")'
            ' + createDataCard("BR Rank", info.rank || "-")'
            ' + createDataCard("BR Max Rank", info.maxRank || "-")'
            ' + createDataCard("BR Points", info.rankingPoints || "-")'
            ' + createDataCard("CS Rank", info.csRank || "-")'
            ' + createDataCard("CS Max Rank", info.csMaxRank || "-")'
            ' + createDataCard("CS Points", info.csRankingPoints || "-")'
            ' + createDataCard("Badges", info.badgeCnt || "0")'
            ' + createDataCard("Likes", info.liked || "0")'
            ' + createDataCard("Created", info.createAt ? new Date(info.createAt*1000).toLocaleDateString() : "-")'
            ' + createDataCard("Last Login", info.lastLoginAt ? new Date(info.lastLoginAt*1000).toLocaleDateString() : "-")'
            ' + \'</div>\';'
            ' if(clan && clan.clanName){'
            '   html+=\'<div style="margin-top:20px; padding:15px; background:rgba(10,10,10,0.5); border-radius:12px;">\';'
            '   html+=\'<h4 style="color:var(--purple-accent); margin-bottom:10px;">Clan Information</h4>\';'
            '   html+=\'<div class="data-grid">\''
            '   + createDataCard("Clan Name", clan.clanName || "-")'
            '   + createDataCard("Clan Level", clan.clanLevel || "-")'
            '   + createDataCard("Members", (clan.memberNum && clan.capacity) ? (clan.memberNum + "/" + clan.capacity) : "-")'
            '   + \'</div></div>\';'
            ' }'
            ' if(social && social.signature){'
            '   html+=\'<div style="margin-top:20px; padding:15px; background:rgba(10,10,10,0.5); border-radius:12px;">\';'
            '   html+=\'<h4 style="color:var(--info-blue); margin-bottom:10px;">Social Info</h4>\';'
            '   html+=\'<p style="color: var(--text-light);">Signature: \' + escapeHtml(social.signature || "-") + \'</p>\';'
            '   html+=\'</div>\';'
            ' }'
            ' html += \'</div>\'; resultsDiv.innerHTML = html; playSound("success");'
            ' } else { resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-exclamation-circle"></i> Player not found or invalid UID</div>\'; playSound("error"); }'
            '} catch(err){ console.error(err); resultsDiv.innerHTML = \'<div style="padding: 20px; background: rgba(220, 38, 38, 0.1); border-radius: 10px; color: var(--primary-red);"><i class="fas fa-times-circle"></i> Error occurred while searching</div>\'; playSound("error"); } }'
            '</script>'
        )
        return get_base_template('FreeFire Stats - OSINT Tool', content, False)

    @app.route('/profile')
    @login_required
    def profile():
        user = db.get_user(session['username'])
        search_logs = db.get_search_logs(session['username'])
        search_count = len(search_logs)
        
        content = (
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.95), rgba(26, 26, 26, 0.8)); padding: 40px; border-radius: 20px; border: 1px solid rgba(220, 38, 38, 0.2);">'
            '<h2 style="color: var(--primary-red); text-align: center; margin-bottom: 30px;">User Profile</h2>'
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0;">'
                '<div style="background: rgba(10, 10, 10, 0.5); padding: 20px; border-radius: 10px; text-align: center;"><div style="font-size: 2rem; color: var(--primary-red); font-weight: 700;">' + session['username'] + '</div><div style="color: var(--text-gray); margin-top: 10px;">Username</div></div>'
                '<div style="background: rgba(10, 10, 10, 0.5); padding: 20px; border-radius: 10px; text-align: center;"><div style="font-size: 2rem; color: var(--success-green); font-weight: 700;">' + str(user.get('credits', 0)) + '</div><div style="color: var(--text-gray); margin-top: 10px;">Credits</div></div>'
                '<div style="background: rgba(10, 10, 10, 0.5); padding: 20px; border-radius: 10px; text-align: center;"><div style="font-size: 2rem; color: var(--info-blue); font-weight: 700;">' + str(search_count) + '</div><div style="color: var(--text-gray); margin-top: 10px;">Searches</div></div>'
            '</div>'
            '<div style="text-align: center; margin: 40px 0;"><p style="color: var(--text-gray);">Your User ID</p><div style="background: rgba(220, 38, 38, 0.1); padding: 15px; border-radius: 10px; margin: 10px 0; font-family: monospace; color: var(--primary-red);">' + user['id'] + '</div></div>'
            '<div style="background: rgba(10, 10, 10, 0.5); padding: 30px; border-radius: 15px;"><h3 style="color: var(--primary-red); margin-bottom: 20px;">Redeem Key</h3>'
            '<form id="redeemForm" style="display: flex; gap: 15px;"><input type="text" id="keyCode" placeholder="Enter key (OSIT-XXXX-XXXX)" style="flex: 1; padding: 14px; background: rgba(10, 10, 10, 0.8); border: 1px solid rgba(220, 38, 38, 0.2); border-radius: 10px; color: white;"><button type="submit" class="btn">Redeem</button></form>'
            '<div id="redeemMessage"></div></div>'
            '<div style="background: rgba(10, 10, 10, 0.5); padding: 30px; border-radius: 15px; margin-top: 20px;"><h3 style="color: var(--primary-red); margin-bottom: 20px;">Account Management</h3>'
            '<div style="text-align: center;"><button id="deleteAccountBtn" class="btn btn-danger" style="margin-right: 10px;"><i class="fas fa-trash-alt"></i> Delete Account</button></div></div>'
            '<div id="deleteConfirmation" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); z-index: 1000; align-items: center; justify-content: center;">'
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.98), rgba(26, 26, 26, 0.95)); padding: 30px; border-radius: 20px; max-width: 500px; width: 90%;">'
            '<h3 style="color: var(--primary-red); margin-bottom: 20px;">Confirm Account Deletion</h3>'
            '<p style="color: var(--text-gray); margin-bottom: 20px;">Are you sure you want to delete your account? This action cannot be undone.</p>'
            '<div style="display: flex; justify-content: center; gap: 15px;">'
            '<button id="confirmDeleteBtn" class="btn btn-danger">Delete Account</button>'
            '<button id="cancelDeleteBtn" class="btn btn-alt">Cancel</button>'
            '</div>'
            '</div>'
            '</div>'
            '</div>'
            '<script>'
            "document.getElementById('redeemForm').addEventListener('submit', async function(e){ e.preventDefault(); playSound('click'); const key=document.getElementById('keyCode').value; const response=await fetch('/api/redeem-key', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({key})}); const data=await response.json(); const msgDiv=document.getElementById('redeemMessage'); if(data.success){ msgDiv.innerHTML='<div style=\"color: var(--success-green); margin-top: 15px;\">Key redeemed! '+data.credits+' credits added.</div>'; showToast('Key redeemed! +' + data.credits + ' credits', 'success'); playSound('success'); setTimeout(()=>location.reload(), 1200);} else { msgDiv.innerHTML='<div style=\"color: var(--primary-red); margin-top: 15px;\">'+(data.error||'Invalid key')+'</div>'; showToast(data.error || 'Invalid key', 'error'); playSound('error'); } });",
            "document.getElementById('deleteAccountBtn').addEventListener('click', function() { document.getElementById('deleteConfirmation').style.display = 'flex'; });",
            "document.getElementById('cancelDeleteBtn').addEventListener('click', function() { document.getElementById('deleteConfirmation').style.display = 'none'; });",
            "document.getElementById('confirmDeleteBtn').addEventListener('click', async function() { playSound('click'); const response=await fetch('/api/delete-account', {method:'POST'}); const data=await response.json(); if(data.success){ showToast('Account deleted successfully', 'success'); playSound('success'); setTimeout(()=>window.location.href='/logout', 1500); } else { showToast(data.error || 'Failed to delete account', 'error'); playSound('error'); } });",
            '</script>'
        )
        return get_base_template('Profile - OSINT Tool', content, False)

    @app.route('/pricing')
    @login_required
    def pricing():
        contact_link = 'https://t.me/BaignX'
        content = (
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div class="header"><h1>Pricing Plans</h1><p style="color: var(--text-gray);">Contact <a href="' + contact_link + '" target="_blank" style="color: var(--primary-red); text-decoration: underline;">@BaignX</a> to purchase credits.</p></div>'
            '<div class="pricing-grid">'
            '<div class="pricing-card"><h3 style="color: var(--primary-red); font-size: 1.5rem;">Starter</h3><div style="font-size: 3rem; color: var(--primary-red); margin: 20px 0;">$5</div><div style="font-size: 1.5rem; color: var(--success-green);">50 Credits</div><ul style="list-style: none; padding: 20px 0; color: var(--text-gray);"><li style="margin: 10px 0;">✓ 25 searches</li><li style="margin: 10px 0;">✓ Valid 30 days</li><li style="margin: 10px 0;">✓ Basic support</li></ul><a class="btn" href="' + contact_link + '" target="_blank" style="width: 100%; display:block; text-align:center;">Contact @BaignX</a></div>'
            '<div class="pricing-card featured"><h3 style="color: var(--primary-red); font-size: 1.5rem;">Basic</h3><div style="font-size: 3rem; color: var(--primary-red); margin: 20px 0;">$10</div><div style="font-size: 1.5rem; color: var(--success-green);">120 Credits</div><ul style="list-style: none; padding: 20px 0; color: var(--text-gray);"><li style="margin: 10px 0;">✓ 60 searches</li><li style="margin: 10px 0;">✓ Valid 30 days</li><li style="margin: 10px 0;">✓ Priority support</li></ul><a class="btn" href="' + contact_link + '" target="_blank" style="width: 100%; display:block; text-align:center;">Contact @BaignX</a></div>'
            '<div class="pricing-card"><h3 style="color: var(--primary-red); font-size: 1.5rem;">Pro</h3><div style="font-size: 3rem; color: var(--primary-red); margin: 20px 0;">$20</div><div style="font-size: 1.5rem; color: var(--success-green);">300 Credits</div><ul style="list-style: none; padding: 20px 0; color: var(--text-gray);"><li style="margin: 10px 0;">✓ 150 searches</li><li style="margin: 10px 0;">✓ Valid 90 days</li><li style="margin: 10px 0;">✓ Premium support</li></ul><a class="btn" href="' + contact_link + '" target="_blank" style="width: 100%; display:block; text-align:center;">Contact @BaignX</a></div>'
            '</div>'
        )
        return get_base_template('Pricing - OSINT Tool', content, False)

    @app.route('/tickets')
    @login_required
    def tickets():
        user = db.get_user(session['username'])
        tickets_data = db.get_tickets()
        user_tickets = []
        for tid, ticket in tickets_data.items():
            if ticket['user_id'] == user['id']:
                ticket['id'] = tid
                user_tickets.append(ticket)
        
        tickets_html = ''
        for ticket in user_tickets:
            tickets_html += (
                '<div class="ticket-card" onclick="window.location.href=\'/ticket/' + ticket['id'] + '\'">'
                '<div style="display: flex; justify-content: space-between; margin-bottom: 10px;">'
                '<span style="color: var(--primary-red);">#' + ticket['id'][:8] + '</span>'
                '<span style="color: var(--text-gray);">' + ticket['status'] + '</span>'
                '</div>'
                '<h3 style="color: white; margin-bottom: 10px;">' + ticket['subject'] + '</h3>'
                '<p style="color: var(--text-gray);">' + (ticket['message'][:100] + '...') + '</p>'
                '</div>'
            )
        
        if not tickets_html:
            tickets_html = '<div style="text-align: center; color: var(--text-gray); padding: 40px;">No tickets found</div>'
        
        content = (
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div class="header"><h1>Support Tickets</h1><button class="btn" onclick="showCreateTicket()">Create Ticket</button></div>'
            '<div id="ticketsList">' + tickets_html + '</div>'
            '<div id="createTicketModal" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 9999; align-items: center; justify-content: center;">'
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.98), rgba(26, 26, 26, 0.95)); padding: 30px; border-radius: 20px; max-width: 500px; width: 90%;">'
            '<h2 style="color: var(--primary-red); margin-bottom: 20px;">Create Ticket</h2>'
            '<form id="ticketForm">'
            '<div class="form-group"><label>Subject</label><input type="text" id="subject" required></div>'
            '<div class="form-group"><label>Message</label><textarea id="message" rows="5" required></textarea></div>'
            '<div style="display: flex; gap: 10px;"><button type="submit" class="btn">Submit</button>'
            '<button type="button" class="btn btn-alt" onclick="hideCreateTicket()">Cancel</button></div>'
            '</form></div></div>'
            '<script>'
            'function showCreateTicket(){ document.getElementById("createTicketModal").style.display = "flex"; }'
            'function hideCreateTicket(){ document.getElementById("createTicketModal").style.display = "none"; }'
            'document.getElementById("ticketForm").addEventListener("submit", async function(e){ e.preventDefault(); playSound("click"); const response=await fetch("/api/create-ticket",{method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ subject: document.getElementById("subject").value, message: document.getElementById("message").value })}); const data=await response.json(); if(data.success){ showToast("Ticket created successfully!", "success"); playSound("success"); location.reload(); } else { showToast("Failed to create ticket", "error"); playSound("error"); } });'
            '</script>'
        )
        return get_base_template('Support Tickets - OSINT Tool', content, False)

    @app.route('/ticket/<ticket_id>')
    @login_required
    def view_ticket(ticket_id):
        tickets_data = db.get_tickets()
        if ticket_id not in tickets_data:
            return redirect('/tickets')
        
        ticket = tickets_data[ticket_id]
        user = db.get_user(session['username'])
        
        if ticket['user_id'] != user['id'] and user.get('role') != 'admin':
            return redirect('/tickets')
        
        replies = db.get_ticket_replies(ticket_id)
        
        replies_html = ''
        for reply in replies:
            attachment_html = ''
            if reply.get('attachment_id'):
                attachment = db.get_ticket_attachment(reply['attachment_id'])
                if attachment:
                    attachment_html = '<div style="margin-top: 10px;"><a href="/api/attachment/' + reply['attachment_id'] + '" target="_blank" style="color: var(--info-blue);"><i class="fas fa-paperclip"></i> ' + attachment['filename'] + '</a></div>'
            
            replies_html += (
                '<div style="background: rgba(10, 10, 10, 0.5); padding: 20px; border-radius: 10px; margin-bottom: 15px;">'
                '<div style="display: flex; justify-content: space-between; margin-bottom: 10px;">'
                '<span style="color: ' + ('var(--primary-red)' if reply.get('is_admin') else 'white') + ';">' + reply['username'] + (' (Admin)' if reply.get('is_admin') else '') + '</span>'
                '<span style="color: var(--text-gray); font-size: 0.9rem;">' + reply.get('created_at', '') + '</span>'
                '</div><p style="color: var(--text-light);">' + reply['message'] + '</p>'
                + attachment_html + '</div>'
            )
        
        reply_form_html = ''
        if user.get('role') == 'admin' or ticket['status'] != 'CLOSED':
            reply_form_html = (
                '<form id="replyForm">'
                '<div class="form-group"><label>Add Reply</label><textarea id="replyMessage" rows="3" required></textarea></div>'
            )
            if user.get('role') == 'admin':
                reply_form_html += (
                    '<div class="form-group">'
                    '<label>Attachment (Optional)</label>'
                    '<div class="file-upload">'
                    '<input type="file" id="attachmentFile" name="attachment">'
                    '<label for="attachmentFile" class="file-upload-label"><i class="fas fa-paperclip"></i> Choose File</label>'
                    '<span id="file-name" style="margin-left: 10px; color: var(--text-gray);">No file chosen</span>'
                    '</div>'
                    '</div>'
                )
            reply_form_html += '<button type="submit" class="btn">Send Reply</button>'
            if user.get('role') == 'admin' and ticket['status'] != 'CLOSED':
                reply_form_html += '<button type="button" class="btn btn-alt" onclick="closeTicket()" style="margin-left: 10px;">Close Ticket</button>'
            reply_form_html += '</form>'
        else:
            reply_form_html = '<div style="text-align: center; color: var(--text-gray);">This ticket is closed</div>'
        
        js_code = '''
        <script>
        const replyForm=document.getElementById("replyForm"); 
        if(replyForm){ 
            replyForm.addEventListener("submit", async function(e){ 
                e.preventDefault();
                playSound('click');
                const formData = new FormData();
                formData.append("ticket_id", "''' + ticket_id + '''");
                formData.append("message", document.getElementById("replyMessage").value);
        '''
        if user.get('role') == 'admin':
            js_code += '''
                const fileInput = document.getElementById("attachmentFile");
                if (fileInput && fileInput.files.length > 0) {
                    formData.append("attachment", fileInput.files[0]);
                }
            '''
        js_code += '''
                const response=await fetch("/api/reply-ticket",{method:"POST", body: formData});
                const r=await response.json(); 
                if(r.success){ 
                    showToast("Reply sent", "success");
                    playSound('success');
                    location.reload(); 
                } else {
                    showToast("Failed to send reply", "error");
                    playSound('error');
                }
            }); 
        }
        const fileInput = document.getElementById("attachmentFile");
        if (fileInput) {
            fileInput.addEventListener("change", function() {
                const fileName = this.files.length > 0 ? this.files[0].name : "No file chosen";
                document.getElementById("file-name").textContent = fileName;
            });
        }
        function closeTicket() {
            if (confirm("Are you sure you want to close this ticket?")) {
                fetch("/api/close-ticket", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ticket_id: "''' + ticket_id + '''"})
                }).then(()=> { showToast("Ticket closed", "success"); playSound('success'); location.reload(); });
            }
        }
        </script>
        '''
        
        content = (
            '<a href="/tickets" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>'
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.95), rgba(26, 26, 26, 0.8)); padding: 40px; border-radius: 20px;">'
            '<div style="display: flex; justify-content: space-between; margin-bottom: 20px;"><h2 style="color: var(--primary-red);">Ticket #' + ticket_id[:8] + '</h2><span style="color: var(--text-gray);">' + ticket['status'] + '</span></div>'
            '<h3 style="color: white; margin-bottom: 20px;">' + ticket['subject'] + '</h3>'
            '<div style="background: rgba(10, 10, 10, 0.5); padding: 20px; border-radius: 10px; margin-bottom: 30px;"><p style="color: var(--text-light);">' + ticket['message'] + '</p></div>'
            + replies_html + reply_form_html + '</div>' + js_code
        )
        return get_base_template('Ticket #' + ticket_id[:8] + ' - OSINT Tool', content, False)

    @app.route('/admin')
    @admin_required
    def admin():
        # Get all users
        users_data = {}
        try:
            all_users = db.data["users"]
            if all_users:
                users_data = all_users
        except Exception as e:
            app.logger.error(f"Error getting users: {str(e)}")
        
        total_credits = sum(user.get('credits', 0) for user in users_data.values())
        active_users = sum(1 for user in users_data.values() if user.get('status') == 'active')
        
        users_table = ''
        for username, user in users_data.items():
            if username != session['username']:
                online_status = "Online" if is_user_online(username) else "Offline"
                status_class = "status-online" if is_user_online(username) else "status-offline"
                users_table += (
                    '<tr>'
                    '<td style="font-family: monospace; font-size: 0.8rem;">' + user['id'][:8] + '...</td>'
                    '<td>' + username + '</td>'
                    '<td>' + user.get('email', '') + '</td>'
                    '<td>' + str(user.get('credits', 0)) + '</td>'
                    '<td>' + (user.get('credits_expiry', 'Never')[:10] if user.get('credits_expiry') else 'Never') + '</td>'
                    '<td><span class="status-badge ' + status_class + '">' + online_status + '</span></td>'
                    '<td>'
                    '<button class="btn" data-u="' + username + '" onclick="addCredits(this.dataset.u)" style="padding: 5px 10px; font-size: 0.8rem;">Add</button> '
                    '<button class="btn" data-u="' + username + '" onclick="removeCredits(this.dataset.u)" style="padding: 5px 10px; font-size: 0.8rem; background: var(--primary-red);">Remove</button> '
                    '<button class="btn btn-alt" data-u="' + username + '" onclick="toggleStatus(this.dataset.u)" style="padding: 5px 10px; font-size: 0.8rem;">' + ('Ban' if user.get('status','active')=='active' else 'Unban') + '</button>'
                    '</td></tr>'
                )
        
        # Admin transfer
        admin_transfer_html = ''
        from config import CONFIG
        if CONFIG['admin_transfer_enabled']:
            admin_options = ''
            for username, user in users_data.items():
                if user.get('role') == 'admin' and username != session['username']:
                    admin_options += f'<option value="{username}">{username}</option>'
            
            admin_transfer_html = (
                '<div class="admin-transfer-container" style="background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8)); padding: 30px; border-radius: 20px; margin-bottom: 30px;">'
                '<h3 style="color: var(--primary-red); margin-bottom: 20px;">Transfer Admin Rights</h3>'
                '<div class="admin-transfer-form" style="display:flex; gap:15px; flex-wrap:wrap;">'
                '<select id="adminSelect" class="form-group" style="flex: 1; min-width:200px;">'
                '<option value="">Select admin to transfer rights to</option>'
                + admin_options +
                '</select>'
                '<button class="btn" onclick="transferAdmin()">Transfer</button>'
                '</div>'
                '<div id="transferMessage"></div>'
                '</div>'
            )
        
        # API Control Panel
        apis_config_data = db.get_apis_config()
        api_rows = ''
        for key, cfg in apis_config_data.items():
            api_rows += (
                '<div class="api-row" style="background: rgba(10,10,10,0.5); padding: 12px; border-radius: 12px; border: 1px solid rgba(220,38,38,0.1);">'
                f'<input type="text" id="api_name_{key}" value="{cfg["name"]}" placeholder="API Name">'
                f'<div><span id="api_toggle_{key}" class="toggle-pill {"toggle-on" if cfg["enabled"] else "toggle-off"}" onclick="toggleApi(\'{key}\')">{ "Enabled" if cfg["enabled"] else "Disabled" }</span></div>'
                f'<input type="text" id="api_url_{key}" value="{cfg["url"]}" placeholder="URL (use {{query}})">'
                f'<input type="text" id="api_msg_{key}" value="{cfg["offline_message"]}" placeholder="Maintenance message">'
                f'<button class="btn" style="padding:8px 16px;" onclick="updateApi(\'{key}\')">Save</button>'
                '</div>'
            )
        api_control_html = (
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.95), rgba(26, 26, 26, 0.8)); padding: 30px; border-radius: 20px; margin-bottom: 30px;">'
            '<h2 style="color: var(--primary-red); margin-bottom: 10px;">API Control Panel</h2>'
            '<p style="color: var(--text-gray); margin-bottom: 15px;">Toggle APIs ON/OFF for maintenance and update their URLs (use {query} placeholder). Changes take effect instantly.</p>'
            + api_rows +
            '</div>'
        )
        
        # Add download button for admin
        download_button = (
            '<div style="margin-bottom: 30px;">'
            '<h2 style="color: var(--primary-red); margin-bottom: 20px;">Data Management</h2>'
            '<div style="display: flex; gap: 15px; margin-bottom: 20px;">'
            '<a href="/api/admin/download-data" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center;"><i class="fas fa-download" style="margin-right: 10px;"></i> Download All Data</a>'
            '</div>'
            '</div>'
        )
        
        content_parts = [
            '<a href="/dashboard" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back</a>',
            '<div class="header"><h1>Admin Panel</h1><div style="color:var(--text-gray);">Manage users, keys, settings and APIs</div></div>',
            api_control_html,
            download_button,
            '<div style="margin-bottom: 30px;">',
            '<h2 style="color: var(--primary-red); margin-bottom: 20px;">Support Tickets</h2>',
            '<div style="display: flex; gap: 15px; margin-bottom: 20px;">',
            '<a href="/admin/tickets" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center;"><i class="fas fa-ticket-alt" style="margin-right: 10px;"></i> Manage Tickets</a>',
            '</div>',
            '</div>',
            '<div style="margin-bottom: 30px;">',
            '<h2 style="color: var(--primary-red); margin-bottom: 10px;">API Protection</h2>',
            '<div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 15px; margin-bottom: 15px;">',
            '<div style="display: flex; justify-content: space-between; align-items: center;">',
            '<div>',
            '<h3 style="color: var(--info-blue); margin-bottom: 5px;">Network Tab Protection</h3>',
            '<p style="color: var(--text-gray); font-size: 0.9rem;">Protects API endpoints from being inspected in browser developer tools</p>',
            '</div>',
            '<div>',
            '<button class="btn" id="apiProtectionToggle" onclick="toggleApiProtection()" style="background: ' + ('var(--success-green)' if CONFIG['api_protection'] else 'var(--primary-red)') + ';">' + ('Enabled' if CONFIG['api_protection'] else 'Disabled') + '</button>',
            '</div>',
            '</div>',
            '</div>',
            admin_transfer_html,
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px;">',
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.95), rgba(26, 26, 26, 0.8)); padding: 25px; border-radius: 15px; text-align: center;"><div style="font-size: 2.2rem; color: var(--primary-red);">' + str(len(users_data)) + '</div><div style="color: var(--text-gray);">Total Users</div></div>',
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.95), rgba(26, 26, 26, 0.8)); padding: 25px; border-radius: 15px; text-align: center;"><div style="font-size: 2.2rem; color: var(--success-green);">' + str(total_credits) + '</div><div style="color: var(--text-gray);">Total Credits</div></div>',
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.95), rgba(26, 26, 26, 0.8)); padding: 25px; border-radius: 15px; text-align: center;"><div style="font-size: 2.2rem; color: var(--info-blue);">' + str(len(db.get_search_logs())) + '</div><div style="color: var(--text-gray);">Total Searches</div></div>',
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.95), rgba(26, 26, 26, 0.8)); padding: 25px; border-radius: 15px; text-align: center;"><div style="font-size: 2.2rem; color: var(--purple-accent);">' + str(active_users) + '</div><div style="color: var(--text-gray);">Active Users</div></div>',
            '</div>',
            '<div style="display:grid; grid-template-columns: 1.2fr .8fr; gap:20px; margin-bottom:30px;">',
            '<div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.95), rgba(26, 26, 26, 0.8)); padding: 30px; border-radius: 20px;">',
            '<h2 style="color: var(--primary-red); margin-bottom: 20px;">Users Management</h2>',
            '<div class="admin-users-table"><table><thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Credits</th><th>Expiry</th><th>Status</th><th>Actions</th></tr></thead><tbody>',
            users_table,
            '</tbody></table></div></div>',
            '<div style="display:grid; gap:20px;">',
            '<div style="background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8)); padding: 20px; border-radius: 20px;">',
            '<h2 style="color: var(--primary-red); margin-bottom: 10px;">Settings</h2>',
            '<div class="form-group"><label>Per Search Cost (credits)</label><input type="number" id="searchCostInput" value="' + str(CONFIG['search_cost']) + '" min="1"></div>',
            '<button class="btn" onclick="saveConfig()">Save Settings</button>',
            '</div>',
            '<div style="background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8)); padding: 20px; border-radius: 20px;">',
            '<h2 style="color: var(--primary-red); margin-bottom: 10px;">Generate Key</h2>',
            '<form id="keyForm" style="display: flex; gap: 10px; flex-wrap:wrap;">',
            '<input type="number" id="keyCredits" placeholder="Credits" required style="flex:1; padding: 14px; background: rgba(10, 10, 10, 0.8); border: 1px solid rgba(220, 38, 38, 0.2); border-radius: 10px; color: white;">',
            '<input type="number" id="keyDays" placeholder="Valid days (0=forever)" style="flex:1; padding: 14px; background: rgba(10, 10, 10, 0.8); border: 1px solid rgba(220, 38, 38, 0.2); border-radius: 10px; color: white;">',
            '<button type="submit" class="btn">Generate</button></form>',
            '<div id="generatedKey" style="margin-top: 12px;"></div>',
            '</div></div></div>',
            '<script>',
            'function addCredits(username){ const amount=prompt("Credits to add:"); if(amount){ fetch("/api/admin/modify-credits",{method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({username, action:"add", amount: parseInt(amount)})}).then(()=>{ showToast("Credits added", "success"); playSound("success"); location.reload(); }); } }',
            'function removeCredits(username){ const amount=prompt("Credits to remove:"); if(amount){ fetch("/api/admin/modify-credits",{method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({username, action:"remove", amount: parseInt(amount)})}).then(()=>{ showToast("Credits removed", "success"); playSound("success"); location.reload(); }); } }',
            'function toggleStatus(username){ fetch("/api/admin/toggle-status",{method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({username})}).then(()=>{ showToast("Status toggled", "success"); playSound("success"); location.reload(); }); }',
            'function saveConfig(){ const v=parseInt(document.getElementById("searchCostInput").value||"0"); if(v>0){ fetch("/api/admin/config",{method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({search_cost: v})}).then(()=>{ showToast("Settings saved", "success"); playSound("success"); location.reload(); }); } else { showToast("Enter a valid cost", "error"); playSound("error"); } }',
            'document.getElementById("keyForm").addEventListener("submit", async function(e){ e.preventDefault(); playSound("click"); const response=await fetch("/api/admin/generate-key",{method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ credits: parseInt(document.getElementById("keyCredits").value), days: parseInt(document.getElementById("keyDays").value || 0) })}); const data=await response.json(); if(data.success){ document.getElementById("generatedKey").innerHTML = "<div style=\'background: rgba(34, 197, 94, 0.2); padding: 12px; border-radius: 10px; color: var(--success-green);\'>Key: " + data.key + "</div>"; showToast("Key generated", "success"); playSound("success"); } else { showToast("Failed to generate key", "error"); playSound("error"); } });',
            'function toggleApiProtection() { fetch("/api/admin/toggle-api-protection", {method:"POST"}).then(response=>response.json()).then(data=>{ if(data.success){ showToast("API protection: " + (data.api_protection ? "Enabled" : "Disabled"), "success"); playSound("success"); location.reload(); } }); }',
            'function transferAdmin() { const adminSelect=document.getElementById("adminSelect"); if(adminSelect.value){ if(confirm("Are you sure you want to transfer admin rights to " + adminSelect.value + "?")){ fetch("/api/admin/transfer-admin",{method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({username: adminSelect.value})}).then(response=>response.json()).then(data=>{ if(data.success){ showToast("Admin rights transferred", "success"); playSound("success"); location.reload(); } else { showToast(data.error||"Failed", "error"); playSound("error"); } }); } } else { showToast("Please select an admin to transfer rights to.", "error"); playSound("error"); } }',
            # API Control Panel handlers
            'function toggleApi(key){ fetch("/api/admin/apis/toggle",{method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({key})}).then(res=>res.json()).then(d=>{ if(d.success){ const pill=document.getElementById("api_toggle_"+key); if(d.enabled){ pill.classList.remove("toggle-off"); pill.classList.add("toggle-on"); pill.textContent="Enabled"; } else { pill.classList.remove("toggle-on"); pill.classList.add("toggle-off"); pill.textContent="Disabled"; } showToast(d.message, "success"); playSound("success"); } else { showToast(d.error||"Failed", "error"); playSound("error"); }}); }',
            'function updateApi(key){ const name=document.getElementById("api_name_"+key).value; const url=document.getElementById("api_url_"+key).value; const msg=document.getElementById("api_msg_"+key).value; fetch("/api/admin/apis/update",{method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({key, name, url, offline_message: msg})}).then(res=>res.json()).then(d=>{ if(d.success){ showToast("API updated", "success"); playSound("success"); } else { showToast(d.error||"Failed to update", "error"); playSound("error"); } }); }',
            '</script>'
        ]
        content = ''.join(content_parts)
        return get_base_template('Admin Panel - OSINT Tool', content, False)

    # Admin Tickets Management
    @app.route('/admin/tickets')
    @admin_required
    def admin_tickets():
        tickets_data = db.get_tickets()
        users_data = db.data["users"]
        
        tickets_html = ''
        for ticket_id, ticket in tickets_data.items():
            username = "Unknown"
            for u, user in users_data.items():
                if user['id'] == ticket['user_id']:
                    username = u
                    break
            
            tickets_html += (
                '<div class="ticket-card" onclick="window.location.href=\'/ticket/' + ticket_id + '\'">'
                '<div style="display: flex; justify-content: space-between; margin-bottom: 10px;">'
                '<span style="color: var(--primary-red);">#' + ticket_id[:8] + '</span>'
                '<span style="color: var(--text-gray);">' + ticket['status'] + '</span>'
                '</div>'
                '<h3 style="color: white; margin-bottom: 10px;">' + ticket['subject'] + '</h3>'
                '<p style="color: var(--text-gray);">User: ' + username + '</p>'
                '<p style="color: var(--text-gray);">' + (ticket['message'][:100] + '...') + '</p>'
                '</div>'
            )
        
        if not tickets_html:
            tickets_html = '<div style="text-align: center; color: var(--text-gray); padding: 40px;">No tickets found</div>'
        
        content = (
            '<a href="/admin" class="btn" onclick="playSound(\'click\')" style="display: inline-flex; align-items: center; margin-bottom: 20px;"><i class="fas fa-arrow-left" style="margin-right: 10px;"></i> Back to Admin</a>'
            '<div class="header"><h1>Support Tickets Management</h1></div>'
            '<div id="ticketsList">' + tickets_html + '</div>'
        )
        return get_base_template('Admin Tickets - OSINT Tool', content, False)