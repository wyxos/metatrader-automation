<script setup>
import axios from 'axios'
import {onMounted, ref} from "vue";

const logs = ref([])

const channels = ref([])

onMounted(() => {
  axios.get('/logs')
    .then(response =>
      logs.value = response.data
    )

  axios.get('/channels')
    .then(response =>
      channels.value = response.data
    )

  setInterval(() => {
    axios.get('/logs')
      .then(response =>
        logs.value = response.data
      )
  }, 5000)
})

const tab = ref('logs')

const excerpt = (text, length = 40) => {
  return text.length > length ? text.substring(0, length) + '...' : text
}

const scrollTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}
</script>

<template>
  <div class="min-h-screen bg-slate-800 text-white antialiased">
    <div class="container mx-auto">
      <h1 class="text-center underline text-xl font-semibold py-10">Metatrader</h1>

      <div>
        <ul class="grid grid-cols-2 w-full text-center">
          <li>
            <button type="button" class="bg-slate-500 w-full py-2" @click="tab = 'logs'" :class="{'!bg-blue-500' : tab === 'logs'}">Logs</button>
          </li>
          <li>
            <button type="button" class="bg-slate-500 w-full py-2" @click="tab = 'channels'" :class="{'!bg-blue-500' : tab === 'channels'}">Channels</button>
          </li>
        </ul>

        <div v-if="tab === 'channels'" class="border-4 border-blue-500">
          <table class="table w-full">
            <thead>
            <tr>
              <th class="px-4 py-2">Name</th>
              <th class="px-4 py-2">ID</th>
              <th class="px-4 py-2">Status</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="channel in channels" :key="channel.id">
              <td class="border px-4 py-2">{{ channel.name }}</td>
              <td class="border px-4 py-2">{{ channel.telegram_id }}</td>
              <td class="border px-4 py-2">
                <o-switch v-model="channel.enabled" :true-value="1" :false-value="0" @change="() => axios.patch('/channel', {id: channel.id, enabled: channel.enabled})"></o-switch>
              </td>
            </tr>
            </tbody>
          </table>
        </div>

        <div v-if="tab === 'logs'" class="border-4 border-blue-500">
          <table class="table w-full">
            <thead>
            <tr>
              <th class="px-4 py-2">Created At</th>
              <th class="px-4 py-2">Status</th>
              <th class="px-4 py-2">Channel</th>
              <th class="px-4 py-2">Message</th>
              <th class="px-4 py-2">Payload Sent</th>
              <td class="px-4 py-2"></td>
            </tr>
            </thead>
            <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td class="border px-4 py-2">{{ log.created_at }}</td>
              <td class="border px-4 py-2"  :class="{'bg-red-500': Boolean(log.exception), 'bg-green-500': log.trade_response !== 'null'}"></td>
              <td class="border px-4 py-2">{{ log.channel }}</td>
              <td class="border px-4 py-2">{{ excerpt(log.message) }}</td>
              <td class="border px-4 py-2">{{ log.trade_response !== "null" ? log.parameters : '' }}</td>
              <td class="border px-4 py-2 text-center">
                <button type="button" class="bg-blue-500 hover:bg-blue-900 p-2 rounded">
                  <i class="fas fa-eye"></i>
                </button>
              </td>
            </tr>
            </tbody>
          </table>
        </div>

<!--        button to scroll back top -->
        <button @click="scrollTop" class="fixed bottom-0 right-0 m-4 bg-blue-500 hover:bg-blue-900 p-2 rounded">
          <i class="fas fa-arrow-up"></i>
        </button>
      </div>
    </div>
  </div>
</template>
