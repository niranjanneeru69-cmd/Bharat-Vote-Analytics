/**
 * BharatVote Analytics — script.js
 * Enhanced for the premium dashboard UI.
 */

function qs(id) { return document.getElementById(id); }

// Auto-compute turnout % based on inputs
function bindTurnout() {
    const vc = parseFloat(qs('votes').value) || 0;
    const el = parseFloat(qs('electors').value) || 1;
    const pct = Math.min((vc / el * 100), 100).toFixed(1);
    qs('turnout').value = pct;
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial bindings
    if (qs('votes')) qs('votes').addEventListener('input', bindTurnout);
    if (qs('electors')) qs('electors').addEventListener('input', bindTurnout);
    if (qs('decade')) qs('decade').addEventListener('change', autoUpdateStats);
    
    // Set initial gauge/donut state
    updateGauge(64.66);
    updateDonut(99.99);
});

function autoUpdateStats() {
    const decade = qs('decade').value;
    if (decadeStats && decadeStats[decade]) {
        qs('electors').value = decadeStats[decade].avg_electors;
        qs('votes').value = decadeStats[decade].avg_votes;
        bindTurnout(); // Re-calculate turnout %
    }
}

async function runPrediction() {
    const btnText = qs('predictBtnText');
    const loader = qs('predictBtnLoader');
    
    // UI Loading state
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');

    const payload = {
        electors:       parseFloat(qs('electors').value),
        votes:          parseFloat(qs('votes').value),
        turnout:        parseFloat(qs('turnout').value),
        marginpct:      parseFloat(qs('marginpct').value),
        margin:         parseFloat(qs('margin').value),
        won:            parseInt(qs('won').value),
        decade:         parseFloat(qs('decade').value),
        con_type:       qs('con_type').value,
        region:         qs('region').value,
        party_type:     qs('party_type').value,
        alliance:       qs('alliance').value,
        era:            qs('era').value,
        // Default DNA features if not in form
        edu_level:      6,
        criminal_cases: 0,
        total_assets:   10000000
    };

    try {
        const resp = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await resp.json();
        
        if (data.success) {
            updateDashboard(data);
        } else {
            showToast("Error: " + data.error);
        }
    } catch (e) {
        showToast("Network Error: " + e.message);
    } finally {
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

function updateDashboard(d) {
    // 1. Safe or Swing Card
    qs('tagSafeSwing').textContent = d.safe_swing;
    qs('tagSafeSwing').className = 'badge ' + (d.safe_swing === 'Safe' ? 'success' : 'swing');
    
    qs('barSafe').style.width = d.safe_prob + '%';
    qs('barSwing').style.width = d.swing_prob + '%';
    qs('valSafe').textContent = d.safe_prob + '%';
    qs('valSwing').textContent = d.swing_prob + '%';

    const insight = (d.safe_swing === 'Swing') 
        ? `With a ${d.swing_prob}% Swing probability, this is a competitive seat where the outcome could easily flip — watch this closely!`
        : `This seat is classified as Safe with a ${d.safe_prob}% probability. The incumbent party has a strong historical advantage here.`;
    qs('insightText').textContent = insight;

    // 2. Predicted Turnout
    qs('valTurnoutMain').textContent = d.predicted_turnout + '%';
    qs('valTurnoutInner').textContent = d.predicted_turnout + '%';
    qs('valMaleTurnout').textContent = d.male_turnout + '%';
    qs('valFemaleTurnout').textContent = d.female_turnout + '%';
    updateGauge(d.predicted_turnout);

    // 3. Win or Loss
    qs('tagWinLoss').textContent = d.win_loss;
    qs('tagWinLoss').className = 'badge ' + (d.win_loss === 'WIN' ? 'success' : 'swing');
    qs('valWin').textContent = d.win_prob + '%';
    qs('valLoss').textContent = d.loss_prob + '%';
    updateDonut(d.win_prob);
}

/**
 * Updates the semi-circle gauge
 * @param {number} value 0-100
 */
function updateGauge(value) {
    const fill = qs('gaugeFill');
    if (!fill) return;
    
    // The stroke-dasharray is 125 for the semi-circle
    // offset = 125 - (125 * value / 100)
    const offset = 125 - (125 * value / 100);
    fill.style.strokeDashoffset = offset;

    // Update color based on value
    let color = 'var(--accent-danger)';
    let label = 'Low';
    if (value >= 75) { color = 'var(--accent-success)'; label = 'Very High'; }
    else if (value >= 65) { color = 'var(--accent-success)'; label = 'High'; }
    else if (value >= 50) { color = 'var(--accent-warning)'; label = 'Moderate'; }
    
    fill.style.stroke = color;
    qs('valTurnoutMain').style.color = color;
    const labelEl = qs('cardTurnout').querySelector('.gauge-text .label');
    if (labelEl) labelEl.textContent = label;
}

/**
 * Updates the donut chart
 * @param {number} value 0-100
 */
function updateDonut(value) {
    const fill = qs('donutFill');
    if (!fill) return;
    
    // stroke-dasharray is 251.2 (2 * PI * 40)
    const offset = 251.2 - (251.2 * value / 100);
    fill.style.strokeDashoffset = offset;
    
    const color = (value > 50) ? 'var(--accent-success)' : 'var(--accent-danger)';
    fill.style.stroke = color;
}

function showToast(msg) {
    const toast = qs('toast');
    toast.textContent = msg;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 4000);
}
