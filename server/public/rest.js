document.addEventListener("DOMContentLoaded", () => {

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Define the 'request' function to handle interactions with the server
  async function server_request(url, data, verb, callback) {
    return fetch(url, {
      credentials: 'same-origin',
      method: verb,
      body: JSON.stringify(data),
      headers: { 'Content-Type': 'application/json' }
    })
      .then(response => response.json())
      .then(response => {
        if (callback)
          callback(response);
      })
      .catch(error => console.error('Error:', error));
  }

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // References to frequently accessed elements
  let main = document.querySelector('main');
  let table = document.querySelector('.table');
  let template = document.querySelector('#new_row');
  let add_form = document.querySelector('form[name=add_user]');
  let edit_form = document.querySelector('form[name=edit_user]');
  let delete_button = document.querySelector('delete_button');
  let save_button = document.querySelector('save_button');

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Handle POST Requests
  add_form.addEventListener('submit', async (event) => {
    // Stop the default form behavior
    event.preventDefault();

    // Submit POST request from the add form
    /*
      1. Grab the data from the input fields
      2. Grab the action and method attributes from the form
      3. Submit a server POST request and when the server responds...
        4. Insert a template row into the table
        5. Update the content of the newly added row with the ID, first_name, and last_name of the user
      6. Remove the alert below this comment block
    */

    let first_name = add_form.querySelector('input[name=first_name').value;
    let last_name = add_form.querySelector('input[name=last_name').value;
    let action = add_form.getAttribute("action");
    let method = add_form.getAttribute("method");

    // console.log(typeof first_name); 
    // console.log(typeof last_name); 

    const data = { "first_name": first_name, "last_name": last_name }

    // console.log(typeof data); 
    // console.log(data);

    // console.log(action); 
    // console.log(method); 

    let response = await server_request(`http://localhost:6543${action}`, data, method);

    console.log(response);

    let row = document.createElement("span");
    // row.innerHTML = resp

    row.querySelector('.row').setAttribute('data-id', response.user_id);
    row.querySelector('.row span:nth-of-type(1)').textContent = response.first_name;
    row.querySelector('.row span:nth-of-type(2)').textContent = response.last_name;

    table.appendChild(row);

    // alert('Feature is incomplete!');

  });

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Handle PUT and DELETE Requests
  main.addEventListener('click', (event) => {

    // Open edit form
    if (event.target.classList.contains('edit_button')) {
      main.dataset.mode = 'editing';

      let row = event.target.closest('.row');
      edit_form.querySelector('input[name=first_name]').value = row.children[1].innerText.trim();
      edit_form.querySelector('input[name=last_name]').value = row.children[2].innerText.trim();
      edit_form.dataset.id = row.dataset.id;
    }

    // Close edit form
    if (event.target.classList.contains('cancel_button')) {
      main.dataset.mode = 'viewing';
    }

    // Submit PUT request from the edit form
    /*
      1. Check if the 'save_button' was the clicked element
      2. Retrieve the ID, first_name, and last_name from the edit form
      3. Submit a server PUT request and when the server responds...
        4. Update the row corresponding to this user with the new data if successful
        5. Switch back the main container's mode to 'viewing'
    */
    save_button.addEventListener('submit', async (event) => {
      event.preventDefault();

      let row = event.target.closest('.row');
      let user_id = row.dataset.id;

      let first_name =  row.children[1].innerText.trim();
      let last_name = row.children[2].innerText.trim();

      const data = { "user_id": user_id, "first_name": first_name, "last_name": last_name}

      await function_request(`http://localhost:6543/users/${user_id}`,data,"PUT");
      main.dataset.mode = 'viewing';
      location.reload(); 


    })

    // Submit DELETE request and delete the row if successful
    /*
      1. Check if the 'delete_button' was the clicked element
      2. Retrieve the ID from the closest row
      3. Submit a server DELETE request and when the server responds...
        4. Remove the row if successful
    */
    delete_button.addEventListener('submit', async (event) => {
    // Stop the default form behavior
    event.preventDefault();

    let row = event.target.closest('.row');
    deleted_id = row.dataset.id;
    const data = { "user_id": deleted_id }

    await function_request(`http://localhost:6543/users/${deleted_id}`,data,"DELETE");
    location.reload();

    });
    
  });

});