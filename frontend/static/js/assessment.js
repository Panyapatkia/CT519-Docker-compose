let currentStep = 1;
const totalSteps = 5;
const stepTitles = {
  1: "ข้อมูลพื้นฐาน",
  2: "ข้อมูลการนอน",
  3: "ไลฟ์สไตล์และกิจกรรม",
  4: "ข้อมูลสุขภาพ",
  5: "ตรวจสอบและประเมินผล"
};

function pct(v){ return Number(v).toFixed(1) + '%'; }
function getBarColor(label){ if(label === 'None') return '#16a34a'; if(label === 'Insomnia') return '#f59e0b'; return '#ef4444'; }
function statusClass(status){ if(status === 'None') return 'none'; if(status === 'Insomnia') return 'insomnia'; return 'apnea'; }

function showStep(step){
  currentStep = step;
  document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
  document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');

  document.querySelectorAll('.step-item').forEach(item => item.classList.remove('active'));
  document.querySelector(`.step-item[data-step-dot="${step}"]`).classList.add('active');

  const progress = Math.round((step / totalSteps) * 100);
  document.getElementById('progressFill').style.width = progress + '%';
  document.getElementById('progressText').textContent = progress + '%';
  document.getElementById('stepLabel').textContent = `ขั้นตอน ${step}/${totalSteps}`;
  document.getElementById('stepTitle').textContent = stepTitles[step];

  document.getElementById('prevBtn').style.display = step === 1 ? 'none' : 'inline-flex';
  document.getElementById('nextBtn').classList.toggle('hidden', step === totalSteps);
  document.getElementById('submitBtn').classList.toggle('hidden', step !== totalSteps);

  if(step === 5) renderReview();
}

function getInputData(){
  const genderEl = document.querySelector('input[name="gender"]:checked');
  return {
    gender: genderEl.value,
    age: document.getElementById('age').value,
    occupation: document.getElementById('occupation').value,
    occ_other: document.getElementById('occOther').value,
    sleep_duration: document.getElementById('sleepDur').value,
    quality_of_sleep: document.getElementById('sleepQual').value,
    physical_activity: document.getElementById('activity').value,
    stress_level: document.getElementById('stress').value,
    daily_steps: document.getElementById('steps').value,
    heart_rate: document.getElementById('hr').value,
    bmi_category: document.getElementById('bmi').value,
    bp_systolic: document.getElementById('bpSys').value,
    bp_diastolic: document.getElementById('bpDia').value
  };
}

function renderReview(){
  const data = getInputData();
  const occupationLabel = data.occupation === '__other__' ? `อาชีพอื่น → ${data.occ_other}` : data.occupation;
  const items = [
    ['เพศ', data.gender === 'Male' ? 'ชาย' : 'หญิง'],
    ['อายุ', data.age + ' ปี'],
    ['อาชีพ', occupationLabel],
    ['ชั่วโมงการนอน', data.sleep_duration + ' ชั่วโมง/คืน'],
    ['คุณภาพการนอน', data.quality_of_sleep + '/10'],
    ['กิจกรรมทางกาย', data.physical_activity + ' นาที/วัน'],
    ['ระดับความเครียด', data.stress_level + '/10'],
    ['จำนวนก้าวต่อวัน', data.daily_steps + ' ก้าว'],
    ['อัตราการเต้นหัวใจ', data.heart_rate + ' bpm'],
    ['BMI Category', data.bmi_category],
    ['ความดันโลหิต', `${data.bp_systolic}/${data.bp_diastolic}`]
  ];

  document.getElementById('reviewBox').innerHTML = items.map(([k,v]) =>
    `<div class="review-item"><span>${k}</span><strong>${v}</strong></div>`
  ).join('');
}

function clearError(){
  const box = document.getElementById('errorBox');
  box.style.display = 'none';
  box.textContent = '';
  document.querySelectorAll('.inline-error').forEach(e => { e.style.display='none'; e.textContent=''; });
}

function showError(message){
  const box = document.getElementById('errorBox');
  box.style.display = 'block';
  box.textContent = message;
}

function validateAll(){
  clearError();
  const data = getInputData();

  const checks = [
    ['age', Number(data.age), 1, 120, 'อายุต้องอยู่ระหว่าง 1 ถึง 120 ปี'],
    ['sleepDur', Number(data.sleep_duration), 0, 24, 'ชั่วโมงการนอนต้องอยู่ระหว่าง 0 ถึง 24'],
    ['sleepQual', Number(data.quality_of_sleep), 1, 10, 'คุณภาพการนอนต้องอยู่ระหว่าง 1 ถึง 10'],
    ['activity', Number(data.physical_activity), 0, 500, 'กิจกรรมทางกายต้องอยู่ระหว่าง 0 ถึง 500 นาที'],
    ['stress', Number(data.stress_level), 1, 10, 'ระดับความเครียดต้องอยู่ระหว่าง 1 ถึง 10'],
    ['steps', Number(data.daily_steps), 0, 100000, 'จำนวนก้าวต่อวันไม่ถูกต้อง'],
    ['hr', Number(data.heart_rate), 20, 250, 'อัตราการเต้นหัวใจไม่ถูกต้อง'],
    ['bpSys', Number(data.bp_systolic), 50, 300, 'ความดันตัวบนไม่ถูกต้อง'],
    ['bpDia', Number(data.bp_diastolic), 20, 200, 'ความดันตัวล่างไม่ถูกต้อง']
  ];

  for (const [id, val, min, max, msg] of checks){
    if(Number.isNaN(val) || val < min || val > max){
      const err = document.getElementById(id + 'Error');
      if(err){ err.style.display='block'; err.textContent=msg; }
      showError(msg);
      return false;
    }
  }

  if(Number(data.bp_systolic) <= Number(data.bp_diastolic)){
    showError('ความดันตัวบนต้องมากกว่าความดันตัวล่าง');
    return false;
  }

  return true;
}

const BMI_CATEGORIES = [
  { max: 18.5, value: 'Normal', label: 'Underweight / Normal', desc: 'ต่ำกว่าเกณฑ์ แต่ในโมเดลจะใช้กลุ่ม Normal' },
  { max: 23.0, value: 'Normal', label: 'Normal · ปกติ', desc: 'BMI 18.5 – 22.9' },
  { max: 25.0, value: 'Normal', label: 'Normal Weight', desc: 'ใกล้เกณฑ์ปกติ' },
  { max: 30.0, value: 'Overweight', label: 'Overweight · น้ำหนักเกิน', desc: 'BMI 25.0 – 29.9' },
  { max: Infinity, value: 'Obese', label: 'Obese · อ้วน', desc: 'BMI ≥ 30.0' }
];

function classifyBMI(bmi){
  for(const c of BMI_CATEGORIES){ if(bmi < c.max) return c; }
  return BMI_CATEGORIES[BMI_CATEGORIES.length - 1];
}

function setupBmiCalculator(){
  const wEl = document.getElementById('weight');
  const hEl = document.getElementById('height');
  function recalc(){
    const w = parseFloat(wEl.value);
    const h = parseFloat(hEl.value);
    if(!w || !h || w < 20 || h < 100){
      document.getElementById('bmiValue').textContent = '—';
      document.getElementById('bmiCatLabel').textContent = 'กรอกน้ำหนัก + ส่วนสูง หรือเลือก BMI Category ด้านล่าง';
      document.getElementById('bmiCatDesc').textContent = '';
      return;
    }
    const bmi = w / Math.pow(h / 100, 2);
    const cat = classifyBMI(bmi);
    document.getElementById('bmiValue').textContent = bmi.toFixed(1);
    document.getElementById('bmiCatLabel').textContent = cat.label;
    document.getElementById('bmiCatDesc').textContent = cat.desc;
    document.getElementById('bmi').value = cat.value;
  }
  wEl.addEventListener('input', recalc);
  hEl.addEventListener('input', recalc);
}

function toggleOtherOccupation(){
  const occ = document.getElementById('occupation').value;
  document.getElementById('otherOccField').classList.toggle('hidden', occ !== '__other__');
}

function fillSampleData(){
  document.getElementById('gM').checked = true;
  document.getElementById('age').value = 35;
  document.getElementById('occupation').value = 'Engineer';
  document.getElementById('sleepDur').value = 7.0;
  document.getElementById('sleepQual').value = 7;
  document.getElementById('activity').value = 60;
  document.getElementById('stress').value = 5;
  document.getElementById('steps').value = 7000;
  document.getElementById('hr').value = 72;
  document.getElementById('bmi').value = 'Normal';
  document.getElementById('bpSys').value = 120;
  document.getElementById('bpDia').value = 80;
  toggleOtherOccupation();
}

function renderList(elId, items){
  const el = document.getElementById(elId);
  el.innerHTML = '';
  if(!items || items.length === 0){
    el.innerHTML = '<li>ยังไม่มีข้อสังเกตเพิ่มเติมในส่วนนี้</li>';
    return;
  }
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    el.appendChild(li);
  });
}

function renderResult(result, input){
  const results = document.getElementById('results');
  results.classList.add('show');

  document.getElementById('verdictCard').dataset.status = result.status || 'None';
  const title = document.getElementById('verdictTitle');
  title.textContent = result.title || result.prediction;
  title.className = 'result-title ' + statusClass(result.status || 'None');

  document.getElementById('verdictDesc').textContent = result.description || '';
  document.getElementById('riskLevel').textContent = result.risk_level || '-';
  document.getElementById('confNum').textContent = result.confidence ? pct(result.confidence) : '—';
  document.getElementById('clinicalNote').textContent = result.clinical_note || '-';

  const occNote = document.getElementById('resolvedOccNote');
  if(input.occupation === '__other__'){
    occNote.textContent = `หมายเหตุ: ระบบใช้อาชีพกลุ่มใกล้เคียงคือ "${result.resolved_occupation_label || result.resolved_occupation}" แทนอาชีพที่ไม่มีใน dataset`;
  } else {
    occNote.textContent = `อาชีพที่ใช้ในการประเมิน: ${result.resolved_occupation_label || result.resolved_occupation}`;
  }

  const probs = result.probabilities || {};
  const displayOrder = result.display_order || Object.keys(probs);
  const probBars = document.getElementById('probBars');
  probBars.innerHTML = '';

  displayOrder
    .filter(label => probs[label] !== undefined)
    .sort((a, b) => probs[b] - probs[a])
    .forEach(label => {
      const value = probs[label];
      const row = document.createElement('div');
      row.className = 'prob-row';
      row.innerHTML = `
        <span class="pl">${label === 'None' ? 'ปกติ (None)' : label}</span>
        <div class="prob-bar"><div class="prob-bar-fill" style="width:${value}%; background:${getBarColor(label)}"></div></div>
        <span class="pv">${pct(value)}</span>
      `;
      probBars.appendChild(row);
    });

  const recs = result.recommendations || {};
  renderList('priorityList', recs.priority || []);
  renderList('monitorList', recs.monitor || []);
  renderList('medicalList', recs.medical || []);
  results.scrollIntoView({behavior:'smooth'});
}

document.addEventListener('DOMContentLoaded', () => {
  showStep(1);
  setupBmiCalculator();
  toggleOtherOccupation();

  document.getElementById('occupation').addEventListener('change', toggleOtherOccupation);
  document.getElementById('sampleBtn').addEventListener('click', fillSampleData);

  document.getElementById('nextBtn').addEventListener('click', () => {
    if(currentStep < totalSteps){
      showStep(currentStep + 1);
    }
  });

  document.getElementById('prevBtn').addEventListener('click', () => {
    if(currentStep > 1){
      showStep(currentStep - 1);
    }
  });

  document.getElementById('assessForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    if(!validateAll()) return;

    const submitBtn = document.getElementById('submitBtn');
    submitBtn.textContent = 'กำลังประเมิน...';
    submitBtn.disabled = true;

    const input = getInputData();

    try{
      const res = await fetch('/predict', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(input)
      });

      const result = await res.json();
      if(!res.ok){
        showError(result.error || 'Prediction failed');
        return;
      }
      renderResult(result, input);
    } catch(err){
      showError('ไม่สามารถเชื่อมต่อกับ Flask backend ได้');
    } finally {
      submitBtn.textContent = 'ประเมินผลด้วยโมเดล';
      submitBtn.disabled = false;
    }
  });
});
