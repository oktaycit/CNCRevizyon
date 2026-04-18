#!/usr/bin/env python3
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from flask import Flask, Response, jsonify, render_template_string, request

from projeler_ai_common import (
    discover_projects,
    goals_summary,
    load_goals,
    load_result_from_path,
    load_result_for_goal,
    now_iso,
    presets_for_project,
    save_goals,
)


app = Flask(__name__)


HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Projeler AI Hub</title>
  <style>
    :root { --ink:#10324a; --muted:#62788a; --line:#d8e1ea; --bg:#f5f8fb; --card:#ffffff; --accent:#0f766e; --warn:#8a5a00; --danger:#9f1239; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:linear-gradient(180deg,#f7fbff,#eef4f8); color:var(--ink); }
    .shell { max-width:1480px; margin:0 auto; padding:24px; }
    .hero { margin-bottom:18px; }
    .hero h1 { margin:0 0 6px; font-size:2rem; }
    .hero p { margin:0; color:var(--muted); }
    .grid { display:grid; grid-template-columns:420px 1fr; gap:20px; align-items:start; }
    .card { background:var(--card); border:1px solid var(--line); border-radius:18px; padding:18px; box-shadow:0 16px 42px rgba(22,48,72,.08); }
    .stats { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:14px; }
    .stat { background:var(--bg); padding:14px; border-radius:12px; }
    .stat strong { display:block; font-size:1.5rem; }
    label { display:block; font-size:.92rem; margin:10px 0 6px; color:#42576a; }
    input, select, textarea, button { width:100%; font:inherit; }
    input, select, textarea { border:1px solid #c7d5e0; border-radius:12px; padding:10px 12px; }
    textarea { min-height:140px; resize:vertical; }
    button { border:0; background:var(--accent); color:#fff; border-radius:999px; padding:12px 16px; font-weight:700; cursor:pointer; margin-top:10px; }
    .goal { border:1px solid var(--line); border-radius:14px; padding:14px; margin-bottom:12px; background:#fbfdff; }
    .meta { display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom:8px; }
    .chip { border-radius:999px; padding:4px 10px; font-size:.78rem; font-weight:700; text-transform:uppercase; }
    .pending { background:#fff1c2; color:#795b00; } .running { background:#dcedff; color:#0b4f71; } .done { background:#daf6e4; color:#0b6a3a; } .failed { background:#ffd8d8; color:#902121; } .canceled { background:#eceff3; color:#4a5568; }
    .subtle { color:var(--muted); font-size:.92rem; }
    .viewer { min-height:260px; background:#0d1f2f; color:#eef6ff; border-radius:14px; padding:16px; overflow:auto; font-size:.95rem; line-height:1.6; }
    .viewer h1, .viewer h2, .viewer h3, .viewer h4 { margin:18px 0 10px; color:#ffffff; line-height:1.3; }
    .viewer h1 { font-size:1.8rem; }
    .viewer h2 { font-size:1.45rem; }
    .viewer h3 { font-size:1.15rem; }
    .viewer p, .viewer ul, .viewer ol { margin:10px 0; }
    .viewer code { font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; background:rgba(255,255,255,.08); padding:2px 6px; border-radius:6px; }
    .viewer pre { background:#081521; color:#eff6ff; padding:14px; border-radius:12px; overflow:auto; font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
    .viewer table { width:100%; border-collapse:collapse; margin:14px 0; font-size:.92rem; }
    .viewer th, .viewer td { border:1px solid rgba(255,255,255,.12); padding:8px 10px; text-align:left; vertical-align:top; }
    .viewer th { background:rgba(255,255,255,.08); }
    .viewer blockquote { margin:12px 0; padding:10px 14px; border-left:4px solid #5eead4; background:rgba(255,255,255,.05); }
    .viewer .meta-block { margin-bottom:16px; padding:12px 14px; border-radius:12px; background:rgba(255,255,255,.06); }
    .viewer .meta-block strong { color:#9dc4ea; }
    .viewer .raw-section { margin-top:16px; }
    .viewer .raw-section h4 { margin-bottom:8px; color:#9dc4ea; }
    .actions { display:flex; gap:8px; margin-top:10px; flex-wrap:wrap; }
    .actions.compact { margin-top:0; }
    .ghost { background:#fff; color:var(--ink); border:1px solid var(--line); }
    .ghost.active { background:var(--ink); color:#fff; border-color:var(--ink); }
    .ghost.danger { border-color:#f3c6d0; color:var(--danger); }
    .preset-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:8px; }
    .preset-btn { border:1px solid var(--line); border-radius:12px; background:#f8fbfd; color:var(--ink); padding:10px; text-align:left; margin:0; }
    .result-section { margin-bottom:14px; }
    .result-section strong { display:block; margin-bottom:6px; color:#9dc4ea; }
    .warning { color:var(--warn); }
    .toolbar { display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; margin:14px 0 10px; }
    .viewer-actions { display:flex; justify-content:flex-end; gap:8px; margin-bottom:10px; }
    .chat-box { margin-top:16px; border-top:1px solid rgba(255,255,255,.12); padding-top:14px; }
    .chat-box textarea { min-height:110px; background:#091726; color:#eef6ff; border:1px solid rgba(255,255,255,.12); }
    .session-banner { margin:10px 0 14px; padding:12px 14px; border-radius:12px; background:#eef8f7; border:1px solid #cfe7e4; color:var(--ink); }
    @media (max-width:980px){ .grid{grid-template-columns:1fr;} .stats{grid-template-columns:repeat(2,minmax(0,1fr));} .preset-grid{grid-template-columns:1fr;} }
  </style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <h1>Projeler AI Hub</h1>
      <p><code>~/Projeler</code> icindeki tum projeler icin ortak hedef kuyrugu, presetler ve AI calisma paneli.</p>
    </div>
    <div class="grid">
      <section class="card">
        <div class="stats" id="stats"></div>
        <form id="goalForm">
          <label>Proje</label>
          <select id="projectName" name="project_name"></select>
          <label>Hazir Presetler</label>
          <div class="preset-grid" id="presetGrid"></div>
          <label>Calisma Modu</label>
          <select name="run_mode" id="runMode">
            <option value="report">Rapor / analiz</option>
            <option value="auto_edit">Otomatik edit</option>
          </select>
          <label>Baslik</label>
          <input name="title" id="goalTitle" placeholder="Orn: irrigation build hatasini incele" required>
          <label>Hedef</label>
          <textarea name="prompt" id="goalPrompt" placeholder="Ajanin bu projede ne yapmasini istedigini yaz." required></textarea>
          <button type="submit">Hedefi Kuyruga Ekle</button>
        </form>
        <p class="subtle" id="message">Worker hedefleri sirayla isler, hata alirsa iki kez daha otomatik dener.</p>
      </section>
      <section class="card">
        <div class="meta">
          <div>
            <h2 style="margin:0 0 4px;">Hedef Kuyrugu</h2>
            <div class="subtle">Tum projeler tek panelde gorunur. Sonuclar kart olarak ayrilir.</div>
          </div>
          <div class="actions">
            <button class="ghost" type="button" id="refreshBtn">Yenile</button>
            <button class="ghost danger" type="button" id="cleanupBtn">Eski Sonuclari Temizle</button>
          </div>
        </div>
        <div class="toolbar">
          <div class="actions compact" id="filterBar">
            <button class="ghost active" type="button" data-filter="all">Tum</button>
            <button class="ghost" type="button" data-filter="pending">Bekleyen</button>
            <button class="ghost" type="button" data-filter="running">Calisiyor</button>
            <button class="ghost" type="button" data-filter="done">Tamamlandi</button>
            <button class="ghost" type="button" data-filter="failed">Hatali</button>
          </div>
          <div class="subtle" id="filterSummary">Tum hedefler gorunuyor.</div>
        </div>
        <div id="goalList"></div>
        <h3>Sonuc</h3>
        <div class="viewer-actions">
          <button class="ghost" type="button" id="downloadBtn">Raporu .md indir</button>
        </div>
        <div class="viewer" id="viewer">Bir hedef sectiginde detay sonucu burada goreceksin.</div>
        <div class="chat-box">
          <div class="session-banner" id="sessionBanner">Bir oturum sec. Yeni oturum acmak icin soldaki formu kullan; secili oturumda mesaj gonderirsen ayni ajanla devam eder.</div>
          <label>Oturuma Mesaj Gonder</label>
          <textarea id="chatInput" placeholder="Secili ajan oturumuna devam mesaji yaz."></textarea>
          <button type="button" id="sendChatBtn">Mesaji Gonder</button>
        </div>
      </section>
    </div>
  </div>
  <script>
    const statsEl = document.getElementById('stats');
    const goalListEl = document.getElementById('goalList');
    const viewerEl = document.getElementById('viewer');
    const formEl = document.getElementById('goalForm');
    const projectSelect = document.getElementById('projectName');
    const messageEl = document.getElementById('message');
    const presetGrid = document.getElementById('presetGrid');
    const goalTitle = document.getElementById('goalTitle');
    const goalPrompt = document.getElementById('goalPrompt');
    const runMode = document.getElementById('runMode');
    const filterBar = document.getElementById('filterBar');
    const filterSummary = document.getElementById('filterSummary');
    const cleanupBtn = document.getElementById('cleanupBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const sessionBanner = document.getElementById('sessionBanner');
    let projects = [];
    let currentFilter = 'all';
    let selectedGoalId = null;

    function esc(value) {
      return String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
    }

    function renderInlineMarkdown(text) {
      return esc(text)
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
    }

    function renderMarkdown(markdown) {
      const source = String(markdown || '').replace(/\\r\\n/g, '\\n');
      const lines = source.split('\\n');
      const html = [];
      let inCode = false;
      let codeLines = [];
      let inList = false;
      let inTable = false;
      let tableRows = [];

      function closeList() {
        if (inList) {
          html.push('</ul>');
          inList = false;
        }
      }

      function flushTable() {
        if (!inTable || tableRows.length === 0) return;
        const rows = tableRows.filter((row) => row.length > 0);
        if (rows.length > 0) {
          const header = rows[0];
          const body = rows.slice(1).filter((row) => !row.every((cell) => /^:?-+:?$/.test(cell.replace(/\\s/g, ''))));
          html.push('<table><thead><tr>' + header.map((cell) => `<th>${renderInlineMarkdown(cell.trim())}</th>`).join('') + '</tr></thead><tbody>');
          body.forEach((row) => {
            html.push('<tr>' + row.map((cell) => `<td>${renderInlineMarkdown(cell.trim())}</td>`).join('') + '</tr>');
          });
          html.push('</tbody></table>');
        }
        inTable = false;
        tableRows = [];
      }

      for (const line of lines) {
        if (line.startsWith('```')) {
          closeList();
          flushTable();
          if (inCode) {
            html.push(`<pre><code>${esc(codeLines.join('\\n'))}</code></pre>`);
            codeLines = [];
            inCode = false;
          } else {
            inCode = true;
          }
          continue;
        }

        if (inCode) {
          codeLines.push(line);
          continue;
        }

        if (line.includes('|')) {
          closeList();
          inTable = true;
          tableRows.push(line.split('|').slice(1, -1));
          continue;
        }

        flushTable();

        if (!line.trim()) {
          closeList();
          continue;
        }

        const heading = line.match(/^(#{1,4})\\s+(.*)$/);
        if (heading) {
          closeList();
          const level = heading[1].length;
          html.push(`<h${level}>${renderInlineMarkdown(heading[2])}</h${level}>`);
          continue;
        }

        const quote = line.match(/^>\\s?(.*)$/);
        if (quote) {
          closeList();
          html.push(`<blockquote>${renderInlineMarkdown(quote[1])}</blockquote>`);
          continue;
        }

        const listItem = line.match(/^\\s*[-*]\\s+(.*)$/);
        if (listItem) {
          if (!inList) {
            html.push('<ul>');
            inList = true;
          }
          html.push(`<li>${renderInlineMarkdown(listItem[1])}</li>`);
          continue;
        }

        closeList();
        html.push(`<p>${renderInlineMarkdown(line)}</p>`);
      }

      closeList();
      flushTable();
      if (inCode) {
        html.push(`<pre><code>${esc(codeLines.join('\\n'))}</code></pre>`);
      }
      return html.join('');
    }

    function renderStats(summary) {
      const counts = summary.counts || {};
      statsEl.innerHTML = [
        ['Projeler', summary.projects || 0],
        ['Bekleyen', counts.pending || 0],
        ['Calisiyor', counts.running || 0],
        ['Tamamlanan', counts.done || 0],
      ].map(([label, value]) => `<div class="stat"><strong>${value}</strong><span>${label}</span></div>`).join('');
    }

    function updateFilterSummary(totalGoals, visibleGoals) {
      const labels = {
        all: 'Tum hedefler',
        pending: 'Bekleyen hedefler',
        running: 'Calisan hedefler',
        done: 'Tamamlanan hedefler',
        failed: 'Hatali hedefler',
        canceled: 'Iptal edilen hedefler'
      };
      filterSummary.textContent = `${labels[currentFilter]} gorunuyor: ${visibleGoals}/${totalGoals}`;
    }

    function setFilter(nextFilter) {
      currentFilter = nextFilter;
      Array.from(filterBar.querySelectorAll('[data-filter]')).forEach((button) => {
        button.classList.toggle('active', button.dataset.filter === currentFilter);
      });
      loadGoals();
    }

    function renderPresets() {
      const selected = projects.find((item) => item.name === projectSelect.value);
      const presets = (selected && selected.presets) || [];
      presetGrid.innerHTML = presets.map((preset) => `
        <button class="preset-btn" type="button" onclick="applyPreset('${esc(preset.id)}')">${esc(preset.label)}</button>
      `).join('') || '<div class="subtle">Bu proje icin preset yok.</div>';
    }

    async function loadProjects() {
      const response = await fetch('/projeler-ai/api/projects');
      const payload = await response.json();
      projects = payload.projects || [];
      projectSelect.innerHTML = projects.map((project) => `<option value="${esc(project.name)}">${esc(project.name)}</option>`).join('');
      renderPresets();
    }

    async function loadGoals() {
      const response = await fetch('/projeler-ai/api/goals');
      const payload = await response.json();
      renderStats(payload.summary);
      const allGoals = payload.goals || [];
      const goals = currentFilter === 'all'
        ? allGoals
        : allGoals.filter((goal) => goal.status === currentFilter);
      updateFilterSummary(allGoals.length, goals.length);
      goalListEl.innerHTML = goals.map((goal) => `
        <article class="goal">
          <div class="meta">
            <div>
              <strong>${esc(goal.title)}</strong>
              <div class="subtle">${esc(goal.project_name)} · ${esc(goal.run_mode)} · deneme:${esc(goal.retry_count || 0)} · ${esc(goal.created_at)}</div>
            </div>
            <span class="chip ${esc(goal.status)}">${esc(goal.status)}</span>
          </div>
          <div class="subtle">${esc(goal.prompt)}</div>
          ${goal.last_error ? `<div class="subtle warning">Son hata: ${esc(goal.last_error)}</div>` : ''}
          ${goal.last_warning ? `<div class="subtle">Uyari: ${esc(goal.last_warning)}</div>` : ''}
          <div class="actions">
            <button class="ghost" type="button" onclick="loadGoal('${esc(goal.id)}')">Sonucu Ac</button>
            ${['failed', 'done', 'canceled'].includes(goal.status) ? `<button class="ghost" type="button" onclick="retryGoal('${esc(goal.id)}')">Yeniden Dene</button>` : ''}
            ${['pending', 'running'].includes(goal.status) ? `<button class="ghost danger" type="button" onclick="cancelGoal('${esc(goal.id)}')">Iptal Et</button>` : ''}
          </div>
        </article>
      `).join('') || '<div class="subtle">Henuz hedef yok.</div>';
    }

    function formatGoal(goal) {
      const result = goal.result && goal.result.result ? goal.result.result : null;
      const lastSuccess = goal.last_success_result && goal.last_success_result.result ? goal.last_success_result.result : null;
      const messages = Array.isArray(goal.messages) ? goal.messages : [];
      const implementationLabels = {
        implemented: 'Uygulandi',
        not_applied: 'Degisiklik yok',
        analysis_only: 'Sadece analiz',
        missing: 'Beyan yok',
        applied: 'Uyguladigini soyluyor',
        uncertain: 'Kararsiz'
      };
      const meta = [
        `<div><strong>Baslik:</strong> ${esc(goal.title)}</div>`,
        `<div><strong>Proje:</strong> ${esc(goal.project_name)}</div>`,
        `<div><strong>Durum:</strong> ${esc(goal.status)}</div>`,
        `<div><strong>Mod:</strong> ${esc(goal.run_mode)}</div>`,
      ];
      if (result && result.system_assessment) {
        meta.push(`<div><strong>Sistem tespiti:</strong> ${esc(implementationLabels[result.system_assessment] || result.system_assessment)}</div>`);
      }
      if (result && result.agent_request_status) {
        meta.push(`<div><strong>Ajan beyani:</strong> ${esc(implementationLabels[result.agent_request_status] || result.agent_request_status)}</div>`);
      }
      if (result && result.agent_evidence) {
        meta.push(`<div><strong>Ajan kaniti:</strong> ${esc(result.agent_evidence)}</div>`);
      }
      if (goal.retry_count) meta.push(`<div><strong>Retry:</strong> ${esc(goal.retry_count)}</div>`);
      if (goal.last_error) meta.push(`<div><strong>Son hata:</strong> ${esc(goal.last_error)}</div>`);
      if (goal.last_warning) meta.push(`<div><strong>Uyari:</strong> ${esc(goal.last_warning)}</div>`);
      if (result && Array.isArray(result.changed_files) && result.changed_files.length) {
        meta.push(`<div><strong>Degisen dosyalar:</strong><br>${result.changed_files.map((item) => esc(item)).join('<br>')}</div>`);
      }

      const sections = [`<div class="meta-block">${meta.join('')}</div>`];
      if (messages.length) {
        const renderedMessages = messages.slice(-10).map((message) => `
          <div class="meta-block">
            <strong>${esc(message.role || 'user')}</strong><br>
            ${renderMarkdown(message.content || '')}
          </div>
        `).join('');
        sections.push(`<div class="raw-section"><h4>Oturum Gecmisi</h4>${renderedMessages}</div>`);
      }
      if (goal.status !== 'done' && lastSuccess) {
        sections.push('<div class="meta-block"><strong>Son basarili sonuc</strong><br>Mevcut deneme basarisiz/iptal olsa da onceki basarili cikti korunuyor.</div>');
        sections.push(renderMarkdown(lastSuccess.stdout || ''));
      }
      if (result && result.stdout) {
        if (goal.status !== 'done' && lastSuccess) {
          sections.push('<div class="raw-section"><h4>Son deneme cikti</h4></div>');
        }
        sections.push(renderMarkdown(result.stdout));
      } else {
        sections.push('<p>Bu hedef icin henuz rapor yok.</p>');
      }
      if (result && result.command) {
        sections.push(`<div class="raw-section"><h4>Komut</h4><pre><code>${esc(result.command)}</code></pre></div>`);
      }
      if (result && result.stderr) {
        sections.push(`<div class="raw-section"><h4>Stderr</h4><pre><code>${esc(result.stderr)}</code></pre></div>`);
      }
      return sections.join('');
    }

    async function loadGoal(id) {
      selectedGoalId = id;
      viewerEl.innerHTML = '<p>Yukleniyor...</p>';
      const response = await fetch(`/projeler-ai/api/goals/${id}`);
      const payload = await response.json();
      sessionBanner.textContent = `Secili oturum: ${payload.goal.title} (${payload.goal.project_name})`;
      viewerEl.innerHTML = formatGoal(payload.goal);
    }

    async function submitGoal(event) {
      event.preventDefault();
      messageEl.textContent = 'Hedef kuyruga ekleniyor...';
      const payload = Object.fromEntries(new FormData(formEl).entries());
      const response = await fetch('/projeler-ai/api/goals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (!response.ok) {
        messageEl.textContent = result.error || 'Hedef eklenemedi.';
        return;
      }
      messageEl.textContent = result.message || 'Hedef eklendi.';
      await loadGoals();
      await loadGoal(result.goal.id);
    }

    async function retryGoal(id) {
      messageEl.textContent = 'Hedef yeniden kuyruğa aliniyor...';
      const response = await fetch(`/projeler-ai/api/goals/${id}/retry`, { method: 'POST' });
      const result = await response.json();
      messageEl.textContent = result.message || result.error || 'Yeniden deneme tamamlanamadi.';
      await loadGoals();
      if (response.ok) await loadGoal(id);
    }

    async function cancelGoal(id) {
      messageEl.textContent = 'Hedef iptal ediliyor...';
      const response = await fetch(`/projeler-ai/api/goals/${id}/cancel`, { method: 'POST' });
      const result = await response.json();
      messageEl.textContent = result.message || result.error || 'Iptal islemi tamamlanamadi.';
      await loadGoals();
      if (response.ok) await loadGoal(id);
    }

    async function cleanupGoals() {
      const raw = window.prompt('Kac gunden eski tamamlanmis/hatali/iptal edilmis sonuclar silinsin?', '7');
      if (raw === null) return;
      const olderThanDays = Number(raw);
      if (!Number.isFinite(olderThanDays) || olderThanDays < 0) {
        messageEl.textContent = 'Gecerli bir gun sayisi gir.';
        return;
      }
      messageEl.textContent = 'Eski sonuclar temizleniyor...';
      const response = await fetch('/projeler-ai/api/goals/cleanup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ older_than_days: olderThanDays })
      });
      const result = await response.json();
      messageEl.textContent = result.message || result.error || 'Temizlik tamamlanamadi.';
      await loadGoals();
      viewerEl.innerHTML = '<p>Bir hedef sectiginde detay sonucu burada goreceksin.</p>';
      sessionBanner.textContent = 'Bir oturum sec. Yeni oturum acmak icin soldaki formu kullan; secili oturumda mesaj gonderirsen ayni ajanla devam eder.';
    }

    async function sendChatMessage() {
      if (!selectedGoalId) {
        messageEl.textContent = 'Once bir oturum sec.';
        return;
      }
      const content = chatInput.value.trim();
      if (!content) {
        messageEl.textContent = 'Bos mesaj gonderemezsin.';
        return;
      }
      messageEl.textContent = 'Mesaj oturuma ekleniyor...';
      const response = await fetch(`/projeler-ai/api/goals/${selectedGoalId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });
      const result = await response.json();
      messageEl.textContent = result.message || result.error || 'Mesaj gonderilemedi.';
      if (!response.ok) return;
      chatInput.value = '';
      await loadGoals();
      await loadGoal(selectedGoalId);
    }

    function applyPreset(presetId) {
      const selected = projects.find((item) => item.name === projectSelect.value);
      const preset = ((selected && selected.presets) || []).find((item) => item.id === presetId);
      if (!preset) return;
      goalTitle.value = preset.title;
      goalPrompt.value = preset.prompt;
      runMode.value = preset.run_mode;
      messageEl.textContent = `Preset secildi: ${preset.label}`;
    }

    filterBar.addEventListener('click', (event) => {
      const button = event.target.closest('[data-filter]');
      if (!button) return;
      setFilter(button.dataset.filter);
    });
    projectSelect.addEventListener('change', renderPresets);
    formEl.addEventListener('submit', submitGoal);
    document.getElementById('refreshBtn').addEventListener('click', loadGoals);
    cleanupBtn.addEventListener('click', cleanupGoals);
    sendChatBtn.addEventListener('click', sendChatMessage);
    downloadBtn.addEventListener('click', () => {
      if (!selectedGoalId) {
        messageEl.textContent = 'Once bir hedef sec.';
        return;
      }
      window.open(`/projeler-ai/api/goals/${selectedGoalId}/report.md`, '_blank');
    });
    window.loadGoal = loadGoal;
    window.applyPreset = applyPreset;
    window.retryGoal = retryGoal;
    window.cancelGoal = cancelGoal;
    window.sendChatMessage = sendChatMessage;
    Promise.all([loadProjects(), loadGoals()]);
    setInterval(loadGoals, 15000);
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/projects")
def api_projects():
    projects = []
    for item in discover_projects():
        enriched = dict(item)
        enriched["presets"] = presets_for_project(item["name"])
        projects.append(enriched)
    return jsonify({"success": True, "projects": projects})


@app.route("/api/goals", methods=["GET"])
def api_goals():
    payload = load_goals()
    goals = list(reversed(payload.get("goals", [])))
    return jsonify({"success": True, "goals": goals, "summary": goals_summary(payload.get("goals", []))})


@app.route("/api/goals", methods=["POST"])
def api_submit_goal():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    project_name = str(data.get("project_name", "")).strip()
    title = str(data.get("title", "")).strip()
    prompt = str(data.get("prompt", "")).strip()
    run_mode = str(data.get("run_mode", "report")).strip() or "report"

    projects = {item["name"]: item["path"] for item in discover_projects()}
    if project_name not in projects:
        return jsonify({"success": False, "error": "Gecersiz proje secimi"}), 400
    if not title or not prompt:
        return jsonify({"success": False, "error": "Baslik ve hedef zorunlu"}), 400
    if run_mode not in ("report", "auto_edit"):
        return jsonify({"success": False, "error": "Gecersiz calisma modu"}), 400

    payload = load_goals()
    goals = payload.setdefault("goals", [])
    goal = {
        "id": uuid.uuid4().hex[:12],
        "session_id": uuid.uuid4().hex[:12],
        "project_name": project_name,
        "project_path": projects[project_name],
        "title": title,
        "prompt": prompt,
        "run_mode": run_mode,
        "status": "pending",
        "retry_count": 0,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "messages": [{
            "role": "user",
            "content": prompt,
            "created_at": now_iso(),
        }],
    }
    goals.append(goal)
    save_goals(payload)
    return jsonify({"success": True, "goal": goal, "message": "Hedef kuyruga eklendi"}), 201


@app.route("/api/goals/<goal_id>")
def api_goal_detail(goal_id: str):
    payload = load_goals()
    goal = next((item for item in payload.get("goals", []) if item.get("id") == goal_id), None)
    if not goal:
        return jsonify({"success": False, "error": "Hedef bulunamadi"}), 404
    result = load_result_for_goal(goal)
    last_success_result = load_result_from_path(goal.get("last_success_result_path"))
    merged = dict(goal)
    merged["result"] = result
    merged["last_success_result"] = last_success_result
    return jsonify({"success": True, "goal": merged})


@app.route("/api/goals/<goal_id>/messages", methods=["POST"])
def api_goal_add_message(goal_id: str):
    payload = load_goals()
    goal = next((item for item in payload.get("goals", []) if item.get("id") == goal_id), None)
    if not goal:
        return jsonify({"success": False, "error": "Oturum bulunamadi"}), 404
    if goal.get("status") == "running":
        return jsonify({"success": False, "error": "Ajan su an calisiyor; bitince yeni mesaj gonder."}), 400

    data: Dict[str, Any] = request.get_json(silent=True) or {}
    content = str(data.get("content", "")).strip()
    if not content:
        return jsonify({"success": False, "error": "Mesaj bos olamaz"}), 400

    goal.setdefault("messages", []).append({
        "role": "user",
        "content": content,
        "created_at": now_iso(),
    })
    goal["prompt"] = content
    goal["status"] = "pending"
    goal["updated_at"] = now_iso()
    goal["last_error"] = None
    goal["last_warning"] = None
    save_goals(payload)
    return jsonify({"success": True, "goal": goal, "message": "Mesaj oturuma eklendi; ajan ayni oturumda devam edecek."})


@app.route("/api/goals/<goal_id>/report.md")
def api_goal_markdown(goal_id: str):
    payload = load_goals()
    goal = next((item for item in payload.get("goals", []) if item.get("id") == goal_id), None)
    if not goal:
        return Response("Hedef bulunamadi\n", status=404, mimetype="text/plain")

    result = load_result_for_goal(goal)
    raw_result = (result or {}).get("result") or {}
    if not raw_result and goal.get("last_success_result_path"):
        raw_result = (load_result_from_path(goal.get("last_success_result_path")) or {}).get("result") or {}
    report = raw_result.get("stdout") or ""
    lines = [
        f"# {goal.get('title', 'Rapor')}",
        "",
        f"- Proje: {goal.get('project_name', '-')}",
        f"- Durum: {goal.get('status', '-')}",
        f"- Mod: {goal.get('run_mode', '-')}",
    ]
    if goal.get("retry_count"):
        lines.append(f"- Retry: {goal.get('retry_count')}")
    if goal.get("last_error"):
        lines.append(f"- Son hata: {goal.get('last_error')}")
    if goal.get("last_warning"):
        lines.append(f"- Uyari: {goal.get('last_warning')}")
    lines.append("")
    lines.append(report or "_Bu hedef icin rapor uretilmemis._")
    if raw_result.get("command"):
        lines.extend(["", "## Komut", "", "```text", str(raw_result["command"]), "```"])
    if raw_result.get("stderr"):
        lines.extend(["", "## Stderr", "", "```text", str(raw_result["stderr"]), "```"])

    filename = f"{goal.get('project_name', 'proje')}-{goal.get('id', 'rapor')}.md"
    body = "\n".join(lines) + "\n"
    return Response(
        body,
        mimetype="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.route("/api/goals/<goal_id>/retry", methods=["POST"])
def api_goal_retry(goal_id: str):
    payload = load_goals()
    goal = next((item for item in payload.get("goals", []) if item.get("id") == goal_id), None)
    if not goal:
        return jsonify({"success": False, "error": "Hedef bulunamadi"}), 404
    if goal.get("status") not in {"done", "failed", "canceled"}:
        return jsonify({"success": False, "error": "Bu durumdaki hedef yeniden denemeye uygun degil"}), 400

    previous_status = goal.get("status")
    previous_result_path = goal.get("result_path")
    previous_finished_at = goal.get("finished_at")
    goal.update({
        "status": "pending",
        "updated_at": now_iso(),
        "started_at": None,
        "finished_at": None,
        "last_error": None,
        "last_warning": None,
        "cancel_requested": False,
    })
    if previous_result_path and previous_status == "done":
        goal["last_success_result_path"] = previous_result_path
        goal["last_success_finished_at"] = previous_finished_at
        goal["last_success_status"] = "done"
    save_goals(payload)
    return jsonify({"success": True, "goal": goal, "message": "Hedef yeniden kuyruga alindi"})


@app.route("/api/goals/<goal_id>/cancel", methods=["POST"])
def api_goal_cancel(goal_id: str):
    payload = load_goals()
    goal = next((item for item in payload.get("goals", []) if item.get("id") == goal_id), None)
    if not goal:
        return jsonify({"success": False, "error": "Hedef bulunamadi"}), 404

    status = goal.get("status")
    if status == "pending":
        goal.update({
            "status": "canceled",
            "updated_at": now_iso(),
            "finished_at": now_iso(),
            "cancel_requested": False,
            "last_error": None,
            "last_warning": "Kullanici tarafindan iptal edildi.",
        })
        save_goals(payload)
        return jsonify({"success": True, "goal": goal, "message": "Bekleyen hedef iptal edildi"})
    if status == "running":
        goal.update({
            "cancel_requested": True,
            "updated_at": now_iso(),
            "last_warning": "Iptal talebi alindi; calisan is tamamlaninca kapatilacak.",
        })
        save_goals(payload)
        return jsonify({"success": True, "goal": goal, "message": "Calisan hedef icin iptal talebi kaydedildi"})
    return jsonify({"success": False, "error": "Bu durumdaki hedef iptal edilemez"}), 400


@app.route("/api/goals/cleanup", methods=["POST"])
def api_goals_cleanup():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    older_than_days = int(data.get("older_than_days", 7) or 7)
    threshold = datetime.now().astimezone() - timedelta(days=max(0, older_than_days))
    removable_statuses = {"done", "failed", "canceled"}

    payload = load_goals()
    kept_goals = []
    removed_count = 0
    removed_results = 0
    for goal in payload.get("goals", []):
        status = goal.get("status")
        updated_at = goal.get("updated_at") or goal.get("finished_at") or goal.get("created_at")
        try:
            goal_time = datetime.fromisoformat(updated_at) if updated_at else datetime.now().astimezone()
        except ValueError:
            goal_time = datetime.now().astimezone()

        if status in removable_statuses and goal_time <= threshold:
            result_path = goal.get("result_path")
            if result_path and os.path.exists(result_path):
                Path(result_path).unlink(missing_ok=True)
                removed_results += 1
            removed_count += 1
            continue
        kept_goals.append(goal)

    payload["goals"] = kept_goals
    save_goals(payload)
    return jsonify({
        "success": True,
        "removed_goals": removed_count,
        "removed_results": removed_results,
        "message": f"{older_than_days} gunden eski {removed_count} hedef temizlendi.",
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
