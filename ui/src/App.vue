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

// Channel filters
const channelFilters = ref({
  name: '',
  enabled: '',
  account_id: '',
  id: ''
})

// Filters
const filters = ref({
  start_date: '',
  end_date: '',
  channel: '',
  status: '',
  is_valid_trade: ''
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

// Fetch channels with filters
const fetchChannels = async () => {
  try {
    const params = { ...channelFilters.value }

    // Remove empty filters
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })

    const response = await axios.get('/channels', { params })
    channels.value = response.data

    // if all channels are enabled, set toggleAll to true
    toggleAll.value = !!channels.value.every(channel => channel.enabled === 1);

    // After channel mappings are loaded, ensure account_id is properly set for each channel
    // This is needed for channels that don't have account_id in the response
    fetchChannelMappings().then(() => {
      channels.value.forEach(channel => {
        if (!channel.account_id) {
          const mapping = channelMappings.value.find(m => m.channel_id === channel.id)
          if (mapping) {
            channel.account_id = mapping.account_id
          }
        }
      })
    })
  } catch (error) {
    console.error('Error fetching channels:', error)
  }
}

// Watch for channel filter changes
watch(channelFilters, () => {
  fetchChannels()
}, { deep: true })

onMounted(() => {
  fetchLogs()
  fetchAccounts()
  fetchChannelMappings()
  fetchChannels()

  // Auto-refresh logs every 5 seconds
  setInterval(() => {
    fetchLogs()
  }, 5000)
})

const tab = ref('logs')
const toggleAll = ref(false)

// Account management
const accounts = ref([])
const showAccountModal = ref(false)
const editingAccount = ref(null)
const newAccount = ref({
  account_name: '',
  server_name: '',
  login_id: '',
  password: ''
})

// Channel-account mappings
const channelMappings = ref([])

// Fetch accounts
const fetchAccounts = async () => {
  try {
    const response = await axios.get('/accounts')
    accounts.value = response.data
  } catch (error) {
    console.error('Error fetching accounts:', error)
  }
}

// Fetch channel-account mappings
const fetchChannelMappings = async () => {
  try {
    const response = await axios.get('/channel-mappings')
    channelMappings.value = response.data
  } catch (error) {
    console.error('Error fetching channel mappings:', error)
  }
}

// Create or update account
const saveAccount = async () => {
  try {
    if (editingAccount.value) {
      // Update existing account
      await axios.put(`/accounts/${editingAccount.value.id}`, newAccount.value)
    } else {
      // Create new account
      await axios.post('/accounts', newAccount.value)
    }

    // Refresh accounts list
    await fetchAccounts()

    // Reset form and close modal
    resetAccountForm()
    showAccountModal.value = false
  } catch (error) {
    console.error('Error saving account:', error)
  }
}

// Delete account
const deleteAccount = async (accountId) => {
  if (!confirm('Are you sure you want to delete this account?')) return

  try {
    await axios.delete(`/accounts/${accountId}`)
    await fetchAccounts()
  } catch (error) {
    console.error('Error deleting account:', error)
  }
}

// Edit account
const editAccount = (account) => {
  editingAccount.value = account
  newAccount.value = { ...account }
  showAccountModal.value = true
}

// Reset account form
const resetAccountForm = () => {
  editingAccount.value = null
  newAccount.value = {
    account_name: '',
    server_name: '',
    login_id: '',
    password: ''
  }
}

// Update channel-account mapping
const updateChannelMapping = async (channelId, accountId) => {
  try {
    await axios.post('/channel-mappings', {
      channel_id: channelId,
      account_id: accountId
    })
    await fetchChannelMappings()
  } catch (error) {
    console.error('Error updating channel mapping:', error)
  }
}

// Get account for channel
const getAccountForChannel = (channelId) => {
  const mapping = channelMappings.value.find(m => m.channel_id === channelId)
  return mapping ? mapping.account_id : null
}

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
        <ul class="grid grid-cols-3 w-full text-center">
          <li>
            <button type="button" class="bg-slate-500 w-full py-2" @click="tab = 'logs'" :class="{'!bg-blue-500' : tab === 'logs'}">Logs</button>
          </li>
          <li>
            <button type="button" class="bg-slate-500 w-full py-2" @click="tab = 'channels'" :class="{'!bg-blue-500' : tab === 'channels'}">Channels</button>
          </li>
          <li>
            <button type="button" class="bg-slate-500 w-full py-2" @click="tab = 'accounts'" :class="{'!bg-blue-500' : tab === 'accounts'}">Accounts</button>
          </li>
        </ul>

        <div v-if="tab === 'channels'" class="border-4 border-blue-500">
          <div class="flex items-center justify-between gap-4 p-4">
            <div class="flex items-center gap-4">
              Toggle <o-switch v-model="toggleAll" @change="onToggleAll"></o-switch>
            </div>
            <div class="text-sm">
              Total Channels: {{ channels.length }}
            </div>
          </div>

          <!-- Filter controls for channels -->
          <div class="p-4 bg-slate-700 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Name</label>
              <input
                type="text"
                v-model="channelFilters.name"
                placeholder="Search by name"
                class="w-full p-2 rounded bg-slate-600 text-white"
              >
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Status</label>
              <select
                v-model="channelFilters.enabled"
                class="w-full p-2 rounded bg-slate-600 text-white"
              >
                <option value="">All</option>
                <option value="1">Enabled</option>
                <option value="0">Disabled</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Account</label>
              <select
                v-model="channelFilters.account_id"
                class="w-full p-2 rounded bg-slate-600 text-white"
              >
                <option value="">All Accounts</option>
                <option value="none">No Account</option>
                <option v-for="account in accounts" :key="account.id" :value="account.id">
                  {{ account.account_name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">ID</label>
              <input
                type="number"
                v-model="channelFilters.id"
                placeholder="Filter by ID"
                class="w-full p-2 rounded bg-slate-600 text-white"
              >
            </div>
          </div>

          <table class="table w-full">
            <thead>
            <tr>
              <th class="px-4 py-2">Name</th>
              <th class="px-4 py-2">ID</th>
              <th class="px-4 py-2">Status</th>
              <th class="px-4 py-2">MetaTrader Account</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="channel in channels" :key="channel.id">
              <td class="border px-4 py-2">{{ channel.name }}</td>
              <td class="border px-4 py-2">{{ channel.telegram_id }}</td>
              <td class="border px-4 py-2">
                <o-switch v-model="channel.enabled" :true-value="1" :false-value="0" @change="onChannelToggle(channel)"></o-switch>
              </td>
              <td class="border px-4 py-2">
                <select
                  v-model="channel.account_id"
                  @change="updateChannelMapping(channel.id, channel.account_id)"
                  class="w-full p-2 rounded bg-slate-600 text-white"
                  :disabled="accounts.length === 0"
                >
                  <option value="">Select Account</option>
                  <option v-for="account in accounts" :key="account.id" :value="account.id">
                    {{ account.account_name }}
                  </option>
                </select>
              </td>
            </tr>
            </tbody>
          </table>
        </div>

        <!-- Accounts Tab -->
        <div v-if="tab === 'accounts'" class="border-4 border-blue-500">
          <div class="p-4 flex justify-between items-center">
            <h2 class="text-xl font-semibold">MetaTrader Accounts</h2>
            <button
              @click="resetAccountForm(); showAccountModal = true"
              class="px-4 py-2 bg-green-500 hover:bg-green-700 rounded"
            >
              <i class="fas fa-plus mr-2"></i> Add Account
            </button>
          </div>

          <table class="table w-full">
            <thead>
              <tr>
                <th class="px-4 py-2">Account Name</th>
                <th class="px-4 py-2">Server Name</th>
                <th class="px-4 py-2">Login ID</th>
                <th class="px-4 py-2">Password</th>
                <th class="px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="account in accounts" :key="account.id">
                <td class="border px-4 py-2">{{ account.account_name }}</td>
                <td class="border px-4 py-2">{{ account.server_name }}</td>
                <td class="border px-4 py-2">{{ account.login_id }}</td>
                <td class="border px-4 py-2">•••••••••</td>
                <td class="border px-4 py-2 flex gap-2 justify-center">
                  <button
                    @click="editAccount(account)"
                    class="px-3 py-1 bg-blue-500 hover:bg-blue-700 rounded"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    @click="deleteAccount(account.id)"
                    class="px-3 py-1 bg-red-500 hover:bg-red-700 rounded"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="accounts.length === 0">
                <td colspan="5" class="border px-4 py-8 text-center">
                  No accounts found. Click "Add Account" to create one.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="tab === 'logs'" class="border-4 border-blue-500">
          <!-- Filter controls -->
          <div class="p-4 bg-slate-700 grid grid-cols-1 md:grid-cols-5 gap-4">
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
            <div>
              <label class="block text-sm font-medium mb-1">Valid Trade</label>
              <select
                v-model="filters.is_valid_trade"
                @change="fetchLogs()"
                class="w-full p-2 rounded bg-slate-600 text-white"
              >
                <option value="">All</option>
                <option value="1">Valid</option>
                <option value="0">Invalid</option>
              </select>
            </div>
          </div>

          <table class="table w-full">
            <thead>
            <tr>
              <th class="px-4 py-2">Created At</th>
              <th class="px-4 py-2">Status</th>
              <th class="px-4 py-2">Channel</th>
              <th class="px-4 py-2">Account</th>
              <th class="px-4 py-2">Message</th>
              <th class="px-4 py-2">Payload Sent</th>
              <td class="px-4 py-2"></td>
            </tr>
            </thead>
            <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td class="border px-4 py-2">{{ log.created_at }}</td>
              <td class="border px-4 py-2" :class="{'bg-red-500': Boolean(log.exception) || (log.trade_response !== 'null' && !JSON.parse(log.trade_response).success), 'bg-green-500': log.trade_response !== 'null' && JSON.parse(log.trade_response).success}"></td>
              <td class="border px-4 py-2">{{ log.channel }}</td>
              <td class="border px-4 py-2">{{ log.account_name }}</td>
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
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
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
                  <p class="text-gray-400">Account:</p>
                  <p>{{ selectedLog.account_name }}</p>
                </div>
                <div>
                  <p class="text-gray-400">Status:</p>
                  <p :class="{'text-red-500': Boolean(selectedLog.exception) || (selectedLog.trade_response !== 'null' && !JSON.parse(selectedLog.trade_response).success), 'text-green-500': selectedLog.trade_response !== 'null' && JSON.parse(selectedLog.trade_response).success}">
                    {{ Boolean(selectedLog.exception) || (selectedLog.trade_response !== 'null' && !JSON.parse(selectedLog.trade_response).success) ? 'Error' : selectedLog.trade_response !== 'null' && JSON.parse(selectedLog.trade_response).success ? 'Success' : 'Pending' }}
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

        <!-- Account Modal -->
        <div v-if="showAccountModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div class="bg-slate-700 rounded-lg shadow-lg max-w-md w-full">
            <div class="p-4 border-b border-slate-600 flex justify-between items-center">
              <h3 class="text-xl font-semibold">{{ editingAccount ? 'Edit Account' : 'Add Account' }}</h3>
              <button @click="showAccountModal = false" class="text-gray-400 hover:text-white">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="p-4">
              <div class="mb-4">
                <label class="block text-sm font-medium mb-1">Account Name</label>
                <input
                  v-model="newAccount.account_name"
                  class="w-full p-2 rounded bg-slate-600 text-white"
                  placeholder="e.g., Blorvax"
                >
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium mb-1">Server Name</label>
                <input
                  v-model="newAccount.server_name"
                  class="w-full p-2 rounded bg-slate-600 text-white"
                  placeholder="e.g., Metatrader"
                >
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium mb-1">Login ID</label>
                <input
                  v-model="newAccount.login_id"
                  class="w-full p-2 rounded bg-slate-600 text-white"
                  placeholder="Enter login ID"
                >
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium mb-1">Password</label>
                <input
                  type="password"
                  v-model="newAccount.password"
                  class="w-full p-2 rounded bg-slate-600 text-white"
                  placeholder="Enter password"
                >
              </div>
            </div>
            <div class="p-4 border-t border-slate-600 flex justify-end gap-2">
              <button
                @click="showAccountModal = false"
                class="px-4 py-2 bg-gray-500 hover:bg-gray-700 rounded"
              >
                Cancel
              </button>
              <button
                @click="saveAccount()"
                class="px-4 py-2 bg-green-500 hover:bg-green-700 rounded"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
