<template>
  <v-card
    width="100%"
    class="available-endpoint pa-0 my-4"
  >
    <v-card-text class="pa-2">
      <v-container class="pa-1">
        <v-row>
          <v-col
            cols="6"
            class="pa-1"
          >
            <v-card class="elevation-0 d-flex flex-column align-center pa-0">
              <p class="ma-0 pt-2 text-h5">
                {{ endpoint.name }}
              </p>
              <p class="ma-0 pb-2 text-body-2">
                {{ endpoint.owner }}
              </p>
            </v-card>
          </v-col>
          <v-col
            cols="4"
            class="pa-1"
          >
            <v-card class="elevation-0 d-flex flex-column align-center pa-0">
              <v-simple-table
                dense
                class="text-center"
              >
                <template #default>
                  <tbody>
                    <tr>
                      <td>{{ userFriendlyEndpointType(endpoint.connection_type) }}</td>
                    </tr>
                    <tr>
                      <td>{{ endpoint.place }}</td>
                    </tr>
                    <tr>
                      <td>{{ endpoint.argument }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card>
          </v-col>
          <v-col
            cols="2"
            class="pa-1"
          >
            <v-card class="elevation-0 d-flex flex-column align-center pa-0">
              <v-icon
                class="ma-1"
              >
                {{ persistent_icon }}
              </v-icon>
              <v-icon
                class="ma-1"
              >
                {{ protected_icon }}
              </v-icon>
              <v-icon
                class="ma-1"
              >
                {{ enabled_icon }}
              </v-icon>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
    <v-speed-dial
      v-if="!endpoint.protected"
      v-model="floating_action_button"
      class="endpoint-edit-fab"
      right
      direction="left"
      transition="slide-y-reverse-transition"
      absolute
    >
      <template #activator>
        <v-btn
          v-model="floating_action_button"
          color="pink"
          dark
          fab
          small
          relative
        >
          <v-icon v-if="floating_action_button">
            mdi-close
          </v-icon>
          <v-icon v-else>
            mdi-pencil
          </v-icon>
        </v-btn>
      </template>
      <v-btn
        color="pink"
        fab
        dark
        small
        relative
        @click="toggleEndpointEnabled"
      >
        <v-icon v-if="endpoint.enabled">
          mdi-lightbulb-off
        </v-icon>
        <v-icon v-else>
          mdi-lightbulb-on
        </v-icon>
      </v-btn>
      <v-btn
        color="red"
        fab
        dark
        small
        relative
        :disabled="endpoint.protected"
        @click="removeEndpoint"
      >
        <v-icon>mdi-delete</v-icon>
      </v-btn>
    </v-speed-dial>
  </v-card>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue'

import autopilot from '@/store/autopilot_manager'
import notifications from '@/store/notifications'
import { AutopilotEndpoint, userFriendlyEndpointType } from '@/types/autopilot'
import { autopilot_service } from '@/types/frontend_services'
import back_axios from '@/utils/api'

export default Vue.extend({
  name: 'EndpointCard',
  props: {
    endpoint: {
      type: Object as PropType<AutopilotEndpoint>,
      required: true,
    },
  },
  data() {
    return {
      userFriendlyEndpointType,
      floating_action_button: false,
      updated_endpoint: this.endpoint,
    }
  },
  computed: {
    persistent_icon(): string {
      return this.endpoint.persistent ? 'mdi-content-save' : 'mdi-content-save-off'
    },
    protected_icon(): string {
      return this.endpoint.protected ? 'mdi-lock' : 'mdi-lock-off'
    },
    enabled_icon(): string {
      return this.endpoint.enabled ? 'mdi-lightbulb-on' : 'mdi-lightbulb-off'
    },
  },
  methods: {
    async removeEndpoint(): Promise<void> {
      autopilot.setUpdatingEndpoints(true)
      await back_axios({
        method: 'delete',
        url: `${autopilot.API_URL}/endpoints`,
        timeout: 10000,
        data: [this.endpoint],
      })
        .catch((error) => {
          const message = `Could not remove endpoint: ${error.message}.`
          notifications.pushError({ service: autopilot_service, type: 'AUTOPILOT_ENDPOINT_DELETE_FAIL', message })
        })
    },
    async toggleEndpointEnabled(): Promise<void> {
      this.updated_endpoint.enabled = !this.updated_endpoint.enabled
      this.updateEndpoint()
    },
    async updateEndpoint(): Promise<void> {
      autopilot.setUpdatingEndpoints(true)
      await back_axios({
        method: 'put',
        url: `${autopilot.API_URL}/endpoints`,
        timeout: 10000,
        data: [this.updated_endpoint],
      })
        .catch((error) => {
          const message = `Could not update endpoint: ${error.message}.`
          notifications.pushError({ service: autopilot_service, type: 'AUTOPILOT_ENDPOINT_UPDATE_FAIL', message })
        })
    },
  },
})
</script>

<style scoped>
.endpoint-edit-fab {
  bottom: 32%;
  left: 96%;
}
</style>
