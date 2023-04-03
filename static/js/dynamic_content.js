addEventListener("scroll", throttle(checkPosition, 150))
addEventListener('resize', throttle(checkPosition, 150))
let element_load = document.getElementsByClassName("container_index")[0]

const queryString = window.location.search
const urlParams = new URLSearchParams(queryString)
let query = urlParams.get('q', 'null')
if (query == '') {
    query = 'null'
}

console.log(query)

element_load.onload = addContent(query, 10)

function word_declension(number, variants) {
    value = number

    if (value % 10 == 1 & value % 100 != 11) {
        variant = 0
    }

    else if ((value % 10 >= 2 & value % 10 <= 4) & (value % 100 < 10 || value % 100 >= 20)) {
        variant = 1 
    }
        
    else {
        variant = 2
    }

    return variants[variant]
}

function throttle(callee, timeout) {
  let timer = null

  return function perform(...args) {
    if (timer) return

    timer = setTimeout(() => {
      callee(...args)

      clearTimeout(timer)
      timer = null
    }, timeout)
  }
}

function addContent(query, count) {
    httpGet(`/api/video/${query}/${count}`).then(
        (value) => {
            var content = JSON.parse(value)["content"];

            console.log(content)


            var content_div = document.getElementById('index_content')

            for (let i = 0; i < content.length; i++) {
                let new_div = document.createElement('div')
                new_div.className = 'card'

                let video = content[i]

                new_div.innerHTML = `<picture class="card_picture">
                                        <source srcset="../static/preview/${video['preview_filename']}">
                                        <img src="../static/preview/${video['preview_filename']}" onclick="location.href = '/watch?v=${video['url_filename']}'" alt="Превью не нашлось">
                                     </picture>

                                     <div class="details">
                                         <div class="avatar" style="margin-left: 5px;">
                                             <img src="../static/icons/${video['channel_icon']}" style="width: 40px; height: auto; float: left; margin-right: 10px; border-radius: 50%;">
                                         </div>

                                         <div class="meta">
                                             <a href="/watch?v=${video['url_filename']}"><h3 style="float: bottom; font-family: Roboto, Arial, sans-serif;">${video['name']}</h3></a>
                                             <a href="/channel/${video['creator_name']}"><h6 style="float: bottom; font-size: 15px; padding-top: 10px; color: rgb(128,128,128); margin-bottom: 0px;">${video['creator_name']}</h6></a>
                                             <h6 style="float: bottom; font-size: 12px; padding-top: 0px; color: rgb(128,128,128);">${video['count_views']} ${word_declension(video['count_views'], ["просмотр", "просмотра", "просмотров"])}</h6>
                                         </div>
                                     </div>`

                content_div.appendChild(new_div)
            }
        }
    )
}

function checkPosition() {
    const scrolled = window.scrollY
    const height = document.body.offsetHeight
    const screenHeight = window.innerHeight

    const threshold = height - screenHeight / 4

    const position = scrolled + screenHeight

    const queryString = window.location.search
    const urlParams = new URLSearchParams(queryString)

    let query = urlParams.get('q', 'null')

    if (query == '') {
        query = 'null'
    }

    if (position >= threshold) {
        addContent(query, 4)
    }
}

function httpGet(theUrl)
{
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()

        xhr.open("GET", theUrl)

        xhr.onload = () => {
            resolve(xhr.response)
        }

        xhr.send()
    })
}
