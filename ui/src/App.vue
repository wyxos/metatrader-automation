<script setup>
import axios from 'axios'
import {onMounted, ref, computed, watch} from "vue";

const logs = ref([])
const pagination = ref({
  total: 0,
  page: 1,
  per_page: 10,
  total_pages: 0
})

const channels = ref([])
const uniqueChannels = computed(() => {
  const channelSet = new Set()
  channels.value.forEach(channel => channelSet.add(channel.name))
  return Array.from(channelSet)
})

// Filters
const filters = ref({
  start_date: '',
  end_date: '',
  channel: '',
  status: ''
})

// Selected log for detail view
const selectedLog = ref(null)
const showDetailModal = ref(false)

// Fetch logs with pagination and filters
const fetchLogs = async () => {
  try {
    const params = {
      page: pagination.value.page,
      per_page: pagination.value.per_page,
      ...filters.value
    }

    // Remove empty filters
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })

    const response = await axios.get('/logs', { params })
    logs.value = response.data.logs
    pagination.value = response.data.pagination
  } catch (error) {
    console.error('Error fetching logs:', error)
  }
}

// Watch for filter changes
watch(filters, () => {
  pagination.value.page = 1 // Reset to first page when filters change
  fetchLogs()
}, { deep: true })

onMounted(() => {
  fetchLogs()

  axios.get('/channels')
    .then(response => {
      channels.value = response.data

      // if all channels are enabled, set toggleAll to true
      toggleAll.value = !!channels.value.every(channel => channel.enabled === 1);
    })

  // Auto-refresh logs every 5 seconds
  setInterval(() => {
    fetchLogs()
  }, 5000)
})

const tab = ref('logs')
const toggleAll = ref(false)

const excerpt = (text, length = 40) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

async function onChannelToggle(channel){
  await axios.patch('/channel', {id: channel.id, enabled: channel.enabled})

  // if all channels are enabled, set toggleAll to true
  toggleAll.value = !!channels.value.every(channel => channel.enabled === 1);
}

async function onToggleAll(value) {
  const targetValue = value.target.checked ? 1 : 0
  console.log('targetValue', value)

  const ids = channels.value
      .filter(c => c.enabled !== targetValue)
      .map(c => c.id)

  if (ids.length === 0) return

  await axios.patch('/channels', { ids, enabled: targetValue })

  // Update local state
  channels.value.forEach(c => {
    if (ids.includes(c.id)) c.enabled = targetValue
  })
}

const scrollTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// Pagination methods
const goToPage = (page) => {
  if (page < 1 || page > pagination.value.total_pages) return
  pagination.value.page = page
  fetchLogs()
}

// View log details
const viewLogDetails = (log) => {
  selectedLog.value = log
  showDetailModal.value = true
}

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}
</script>

<template>
  <div class="min-h-screen bg-slate-800 text-white antialiased">
    <div class="container mx-auto flex flex-col">
      <h1 class="text-center underline text-xl font-semibold mb-4 mt-10 block">A.U.T.O.</h1>
      <p class="text-center mb-10">Automated Uptake of Telegram Orders</p>
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
          <div class="flex items-center gap-4 p-4">
            Toggle <o-switch v-model="toggleAll" @change="onToggleAll"></o-switch>
          </div>

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
                <o-switch v-model="channel.enabled" :true-value="1" :false-value="0" @change="onChannelToggle(channel)"></o-switch>
              </td>
            </tr>
            </tbody>
          </table>
        </div>

        <div v-if="tab === 'logs'" class="border-4 border-blue-500">
          <!-- Filter controls -->
          <div class="p-4 bg-slate-700 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Start Date</label>
              <input
                type="date"
                v-model="filters.start_date"
                @input="fetchLogs()"
                class="w-full p-2 rounded bg-slate-600 text-white"
              >
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">End Date</label>
              <input
                type="date"
                v-model="filters.end_date"
                @input="fetchLogs()"
                class="w-full p-2 rounded bg-slate-600 text-white"
              >
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Channel</label>
              <select
                v-model="filters.channel"
                @change="fetchLogs()"
                class="w-full p-2 rounded bg-slate-600 text-white"
              >
                <option value="">All Channels</option>
                <option v-for="channel in uniqueChannels" :key="channel" :value="channel">
                  {{ channel }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Status</label>
              <select
                v-model="filters.status"
                @change="fetchLogs()"
                class="w-full p-2 rounded bg-slate-600 text-white"
              >
                <option value="">All Status</option>
                <option value="success">Success</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>

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
              <td class="border px-4 py-2" :class="{'bg-red-500': Boolean(log.exception), 'bg-green-500': log.trade_response !== 'null'}"></td>
              <td class="border px-4 py-2">{{ log.channel }}</td>
              <td class="border px-4 py-2">{{ excerpt(log.message) }}</td>
              <td class="border px-4 py-2">{{ log.trade_response !== "null" ? log.parameters : '' }}</td>
              <td class="border px-4 py-2 text-center">
                <button
                  type="button"
                  class="bg-blue-500 hover:bg-blue-900 p-2 rounded"
                  @click="viewLogDetails(log)"
                >
                  <i class="fas fa-eye"></i>
                </button>
              </td>
            </tr>
            </tbody>
          </table>

          <!-- Pagination controls -->
          <div class="p-4 flex justify-between items-center bg-slate-700">
            <div>
              Showing {{ logs.length }} of {{ pagination.total }} entries
            </div>
            <div class="flex gap-2">
              <button
                @click="goToPage(1)"
                class="px-3 py-1 rounded bg-blue-500 hover:bg-blue-700 disabled:opacity-50"
                :disabled="pagination.page === 1"
              >
                First
              </button>
              <button
                @click="goToPage(pagination.page - 1)"
                class="px-3 py-1 rounded bg-blue-500 hover:bg-blue-700 disabled:opacity-50"
                :disabled="pagination.page === 1"
              >
                Prev
              </button>
              <span class="px-3 py-1">Page {{ pagination.page }} of {{ pagination.total_pages }}</span>
              <button
                @click="goToPage(pagination.page + 1)"
                class="px-3 py-1 rounded bg-blue-500 hover:bg-blue-700 disabled:opacity-50"
                :disabled="pagination.page === pagination.total_pages"
              >
                Next
              </button>
              <button
                @click="goToPage(pagination.total_pages)"
                class="px-3 py-1 rounded bg-blue-500 hover:bg-blue-700 disabled:opacity-50"
                :disabled="pagination.page === pagination.total_pages"
              >
                Last
              </button>
            </div>
          </div>
        </div>

        <!-- Log Detail Modal -->
        <div v-if="showDetailModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div class="bg-slate-700 rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div class="p-4 border-b border-slate-600 flex justify-between items-center">
              <h3 class="text-xl font-semibold">Log Details</h3>
              <button @click="showDetailModal = false" class="text-gray-400 hover:text-white">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="p-4" v-if="selectedLog">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p class="text-gray-400">ID:</p>
                  <p>{{ selectedLog.id }}</p>
                </div>
                <div>
                  <p class="text-gray-400">Created At:</p>
                  <p>{{ formatDate(selectedLog.created_at) }}</p>
                </div>
                <div>
                  <p class="text-gray-400">Channel:</p>
                  <p>{{ selectedLog.channel }}</p>
                </div>
                <div>
                  <p class="text-gray-400">Status:</p>
                  <p :class="{'text-red-500': Boolean(selectedLog.exception), 'text-green-500': selectedLog.trade_response !== 'null'}">
                    {{ Boolean(selectedLog.exception) ? 'Error' : selectedLog.trade_response !== 'null' ? 'Success' : 'Pending' }}
                  </p>
                </div>
              </div>

              <div class="mb-4">
                <p class="text-gray-400">Message:</p>
                <pre class="bg-slate-800 p-3 rounded overflow-x-auto">{{ selectedLog.message }}</pre>
              </div>

              <div class="mb-4" v-if="selectedLog.parameters">
                <p class="text-gray-400">Parameters:</p>
                <pre class="bg-slate-800 p-3 rounded overflow-x-auto">{{ selectedLog.parameters }}</pre>
              </div>

              <div class="mb-4" v-if="selectedLog.trade_response && selectedLog.trade_response !== 'null'">
                <p class="text-gray-400">Trade Response:</p>
                <pre class="bg-slate-800 p-3 rounded overflow-x-auto">{{ selectedLog.trade_response }}</pre>
              </div>

              <div class="mb-4" v-if="selectedLog.exception">
                <p class="text-gray-400">Exception:</p>
                <pre class="bg-slate-800 p-3 rounded overflow-x-auto text-red-500">{{ selectedLog.exception }}</pre>
              </div>
            </div>
            <div class="p-4 border-t border-slate-600">
              <button @click="showDetailModal = false" class="px-4 py-2 bg-blue-500 hover:bg-blue-700 rounded">
                Close
              </button>
            </div>
          </div>
        </div>

        <!-- Button to scroll back top -->
        <button @click="scrollTop" class="fixed bottom-0 right-0 m-4 bg-blue-500 hover:bg-blue-900 p-2 rounded">
          <i class="fas fa-arrow-up"></i>
        </button>
      </div>
    </div>
  </div>
</template>
