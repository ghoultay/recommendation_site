const one = document.getElementById('star0')
const two = document.getElementById('star1')
const three = document.getElementById('star2')
const four = document.getElementById('star3')
const five = document.getElementById('star4')
const user_id = JSON.parse(document.getElementById('user_id').textContent)

// get the form, confirm-box and csrf token
const form = document.querySelector('.rate-form')
const jumbotron = document.querySelector('.jumbotron')
const confirmBox = document.getElementById('confirm-box')
const csrf = document.getElementsByName('csrfmiddlewaretoken')


jumbotron.addEventListener('mouseleave', () => {
    // Reset the star ratings to their original state
    // Pass the currently selected star's size to maintain the selection state
    const children = form.children
    for (let i=0; i < children.length; i++){
        if(children[i].classList.contains('full')){
            children[i].classList.add("checked")
        }
        if(children[i].classList.contains('halfed')){
            children[i].classList.add('fa-star-half-o')
            children[i].classList.add("checked")
        }
        if(children[i].classList.contains('empty')){
            children[i].classList.add('fa-star-o')
            children[i].classList.remove("checked")
        }
    }
});

const handleStarSelect = (size) => {
    
    const children = form.children
    for (let i=0; i < children.length; i++) {
        if(i <= size) {
            if(children[i].classList.contains('halfed')){
               children[i].classList.remove('fa-star-half-o')
               children[i].classList.add('fa-star')
            }
            if(children[i].classList.contains('empty')){
                children[i].classList.remove('fa-star-o')
                children[i].classList.add('fa-star')
             }  
            children[i].classList.add('checked')
        } else {
            if(children[i].classList.contains('halfed')){
                children[i].classList.remove('fa-star')
                children[i].classList.add('fa-star-half-o')
             }
             if(children[i].classList.contains('empty')){
                 children[i].classList.remove('fa-star')
                 children[i].classList.add('fa-star-o')
              }  
            children[i].classList.remove('checked')
        }
        if(i == 'aboba'){

        }
    }
}

const handleSelect = (selection) => {
    switch(selection){
        case 'star0': {
            handleStarSelect(1)
            return
        }
        case 'star1': {
            handleStarSelect(2)
            return
        }
        case 'star2': {
            handleStarSelect(3)
            return
        }
        case 'star3': {
            handleStarSelect(4)
            return
        }
        case 'star4': {
            handleStarSelect(5)
            return
        }
        default: {
            handleStarSelect(0)
        }
    }

}

const getNumericValue = (stringValue) =>{
    let numericValue;
    if (stringValue === 'star0') {
        numericValue = 1
    } 
    else if (stringValue === 'star1') {
        numericValue = 2
    }
    else if (stringValue === 'star2') {
        numericValue = 3
    }
    else if (stringValue === 'star3') {
        numericValue = 4
    }
    else if (stringValue === 'star4') {
        numericValue = 5
    }
    else {
        numericValue = 0
    }
    return numericValue
}

if (one) {
    const arr = [one, two, three, four, five]

    arr.forEach(item=> item.addEventListener('mouseover', (event)=>{
        handleSelect(event.target.id)
    }))

    arr.forEach(item=> item.addEventListener('click', (event)=>{
        // value of the rating not numeric
        const val = event.target.id
        
        let isSubmit = false
        form.addEventListener('submit', e=>{
            e.preventDefault()
            if (isSubmit) {
                return
            }
            isSubmit = true
            // movie id
            const id = e.target.id
            // value of the rating translated into numeric
            const val_num = getNumericValue(val)

            $.ajax({
                type: 'POST',
                url: "/films/" + (id) + "/",
                data: {
                    'csrfmiddlewaretoken': csrf[0].value,
                    'val': val_num,
                },
                success: function(response){
                    confirmBox.innerHTML = `<p>Successfully rated with ${response.score}</p>`
                },
                error: function(error){
                    console.log(error)
                    confirmBox.innerHTML = '<p>Regiter or log in to do it</p>'
                }
            })
        })
    }))
}