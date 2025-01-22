let getNetPay = (e) => {
  e.target.disabled = true
  e.target.style.color = '#95a5a6'
  let formEl = document.getElementById('paycheck-calculator-form')
  let csrfInputEl = document.getElementById('csrf_token')
  const formData = new FormData(formEl)
  let reqJson = {}

  for (const entry of formData.entries()) {
    reqJson[entry[0]] = entry[1]
  }

  reqJson['user_id'] = USER_ID

  fetch('http://127.0.0.1:5000/paycheck-calculator', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfInputEl.value,
    },
    body: JSON.stringify(reqJson),
  })
    .then((res) => {
      if (res.status == 200) {
        return res.json()
      } else {
        throw new Error('Oh hell naw!')
      }
    })
    .then((json) => {
      document.getElementById('netpay').innerHTML = json.netPay.toLocaleString()
      document.getElementById('grosspay').innerHTML =
        json.grossPay.toLocaleString()
      document.getElementById('withheld').innerHTML = (
        ((json.grossPay - json.netPay) / json.grossPay) *
        100
      ).toLocaleString()
      e.target.style.background = '#27ae60'
      e.target.style.color = '#ecf0f1'
      setTimeout(() => {
        e.target.disabled = false
        e.target.style.background = null
        e.target.style.color = null
      }, 2000)
    })
    .catch((err) => {
      console.log(err)
      e.target.style.background = '#e74c3c'
      e.target.style.color = '#ecf0f1'
      setTimeout(() => {
        e.target.disabled = false
        e.target.style.background = null
        e.target.style.color = null
      }, 2000)
    })
}

window.onload = () => {
  calculateBtnEl = document.querySelector("input[value='Calculate']")
  calculateBtnEl.addEventListener('click', getNetPay)
}
