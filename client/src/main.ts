import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";
import "./assets/main.css"
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

import App from './App.vue'
import router from './router'

const app = createApp(App)


import { 
    faChevronDown,
    faCircle, faEllipsisVertical, 
    faMagnifyingGlass, faPlus, faSort, 
    faSquarePhone, faSquarePlus, faUsers, faVideo,
    faMicrophone,faFaceSmile,faArrowLeft,
    faFile,faImages,faCamera, faUser,
    faSquarePollVertical,faCircleXmark,
    faBell, faStar, faArrowRotateRight,
    faLock,faTrash,faBan, faVideoCamera,
    faThumbsDown, faCheckDouble, faCheck, faImage, faPen,
    faCalendar,
    faTrophy,
    faFutbol,
    faHome,
    faRankingStar

} from '@fortawesome/free-solid-svg-icons'

library.add(
    faUsers, faCircle,faUser, faCalendar, faUsers, faTrophy,
    faSquarePlus, faEllipsisVertical, faPlus,
    faSort, faMagnifyingGlass,
    faChevronDown, faVideo, faThumbsDown,
    faSquarePhone, faMicrophone, faVideoCamera, faRankingStar,
    faHome, faArrowLeft,faTrash,
    faFile, faImages, faCamera,faBan,faImage, faFutbol,
    faSquarePollVertical, faCircleXmark, faBell, faPen,
    faStar, faArrowRotateRight, faLock, faCheckDouble, faCheck
)

app.component('font-awesome-icon', FontAwesomeIcon)
app.use(Toast);
app.use(createPinia())
app.use(router)

app.mount('#app')
