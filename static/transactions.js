var currentTr = null

var handleRowDblClick = function () {
  $('#transaction-update-form')
    .find('input[name="name"]')
    .val($(this).find('td')[0].innerHTML)
  $('#transaction-update-form')
    .find('input[name="amount"]')
    .val($(this).find('td')[1].innerHTML)
  $('#transaction-update-form')
    .find('input[name="day_of_month"]')
    .val($(this).find('td')[2].innerHTML)
  $('#transaction-update-form')
    .find('input[name="is_credit"]')
    .attr('checked', $(this).find('td')[3].innerHTML == 'True' ? true : false)

  currentTr = $(this)

  $('#my_modal_3')[0].showModal()
}

$(window).on('load', function () {
  $('#transaction-add-form').on('submit', function (event) {
    event.preventDefault()

    let transactionAddForm = document.getElementById('transaction-add-form')

    let formData = new FormData(transactionAddForm)
    let reqJson = {}

    for (const entry of formData.entries()) {
      reqJson[entry[0]] = entry[1]
    }

    $.ajax({
      type: 'POST',
      url: '/transactions',
      headers: {
        'X-CSRF-Token': reqJson['csrf_token'],
        'Content-Type': 'application/json',
      },
      data: JSON.stringify(reqJson),
      success: function (res) {
        let newTr = $('<tr></tr>').addClass('hover')
        newTr.append($('<td>' + res.transaction.name + '</td>'))
        newTr.append(
          $('<td>' + parseFloat(res.transaction.amount).toFixed(2) + '</td>')
        )
        newTr.append($('<td>' + res.transaction.day_of_month + '</td>'))
        newTr.append(
          $(`<td>${res.transaction.is_credit == null ? 'False' : 'True'}</td>`)
        )
        newTr.on('dblclick', handleRowDblClick)
        $('#transactions-tbody').append(newTr)
      },
      error: function (err) {
        console.log(err)
      },
    })
  })

  $('#transaction-del-form').on('submit', function (event) {
    event.preventDefault()

    let transactionDelForm = document.getElementById('transaction-del-form')

    let formData = new FormData(transactionDelForm)
    let reqJson = {}

    for (const entry of formData.entries()) {
      reqJson[entry[0]] = entry[1]
    }

    $.ajax({
      type: 'DELETE',
      url: '/transactions',
      headers: {
        'X-CSRF-Token': reqJson['csrf_token'],
      },
      success: function (res) {
        $('#transactions-tbody').html('')
      },
      error: function (err) {
        console.log(err)
      },
    })
  })

  $('#transaction-update-form').on('submit', function (event) {
    event.preventDefault()

    isDeleting = event.originalEvent.submitter.defaultValue == 'Delete'

    let transactionUpdateForm = document.getElementById(
      'transaction-update-form'
    )

    let formData = new FormData(transactionUpdateForm)
    let reqJson = {}

    for (const entry of formData.entries()) {
      reqJson[entry[0]] = entry[1]
    }

    if (isDeleting) {
      reqJson['name'] = currentTr.find('td')[0].innerHTML
      reqJson['amount'] = currentTr.find('td')[1].innerHTML

      $.ajax({
        type: 'DELETE',
        url: '/transactions',
        headers: {
          'X-CSRF-Token': reqJson['csrf_token'],
          'Content-Type': 'application/json',
        },
        data: JSON.stringify(reqJson),
        success: function (res) {
          let targetRows = $('tr.hover').filter(function () {
            return (
              $(this).find(`td:contains('${reqJson['name']}')`).length > 0 &&
              $(this).find(`td:contains('${reqJson['amount']}')`).length > 0
            )
          })

          targetRows.each(function (row) {
            $(this).remove()
          })

          $('#my_modal_3')[0].close()
        },
        error: function (err) {
          console.log(err)
        },
      })
    } else {
      reqJson['old_name'] = currentTr.find('td')[0].innerHTML
      reqJson['old_amount'] = currentTr.find('td')[1].innerHTML

      $.ajax({
        type: 'PUT',
        url: '/transactions',
        headers: {
          'X-CSRF-Token': reqJson['csrf_token'],
          'Content-Type': 'application/json',
        },
        data: JSON.stringify(reqJson),
        success: function (res) {
          let targetRows = $('tr.hover').filter(function () {
            return (
              $(this).find(`td:contains('${reqJson['old_name']}')`).length >
                0 &&
              $(this).find(`td:contains('${reqJson['old_amount']}')`).length > 0
            )
          })

          targetRows.each(function (row) {
            $(this).find('td')[0].innerHTML = res.transaction.name
            $(this).find('td')[1].innerHTML = parseFloat(
              res.transaction.amount
            ).toFixed(2)
            $(this).find('td')[2].innerHTML = res.transaction.day_of_month
            $(this).find('td')[3].innerHTML =
              res.transaction.is_credit == null ? 'False' : 'True'
          })

          $('#my_modal_3')[0].close()
        },
        error: function (err) {
          console.log(err)
        },
      })
    }
  })

  $('tr.hover').on('dblclick', handleRowDblClick)
})
