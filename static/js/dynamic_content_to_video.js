let element_load_1 = document.getElementById('icon')
addEventListener("scroll", throttle(checkPosition, 150))
addEventListener('resize', throttle(checkPosition, 150))
element_load_1.onload = addContent("null", 20)

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


            var content_div = document.getElementById('index_content_video')

            for (let i = 0; i < content.length; i++) {
                let new_div = document.createElement('div')
                new_div.className = 'card_watch'

                let video = content[i]

                new_div.innerHTML = `
                                     <div>
                                         <picture class="card_picture_watch">
                                            <source srcset="../static/preview/${video['preview_filename']}">
                                            <img src="../static/preview/${video['preview_filename']}" onclick="location.href = '/watch?v=${video['filename']}'" alt="Превью не нашлось">
                                         </picture>

                                         <div class="details">


                                             <div class="meta">
                                                 <a href="/watch?v=${video['url_filename']}"><h3 style="float: bottom; font-size: 18px; font-family: Roboto, Arial, sans-serif;">${video['name']}</h3></a>
                                                 <a href="${video['url_channel']}"><h6 style="float: top; font-size: 13px; padding-top: 10px; color: rgb(128,128,128); margin-bottom: 0px;">${video['creator_name']}</h6></a>
                                                 <h6 style="float: bottom; font-size: 10px; padding-top: 0px; color: rgb(128,128,128);">${video['count_views']} ${word_declension(video['count_views'], ["просмотр", "просмотра", "просмотров"])}</h6>
                                             </div>
                                         </div>
                                     </div>
                                     `

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
        addContent(query, 3)
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
