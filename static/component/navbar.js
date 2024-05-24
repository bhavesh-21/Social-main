export default {
  template: `
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">

            <a v-if="this.$store.state.login" class="navbar-brand hand" @click="goto('/feed')">
                <img src="/static/images/blog-white.png" width="30" height="30" class="d-inline-block align-top" alt="">
                Social Connect
            </a>
            <a v-else class="navbar-brand hand" @click="goto('/')">
                <img src="/static/images/blog-white.png" width="30" height="30" class="d-inline-block align-top" alt="">
                Social Connect
            </a>

            <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false"
                aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav mr-auto mb-2 mb-lg-0" style="margin-left: auto;">

                    <div v-if="this.$store.state.login && route==='Search User'" class="d-flex mb-2 mt-2 px-2">
                        <div class="input-group">
                            <input type="search" v-model="query" id="query" placeholder="Search User" ria-label="Search"
                                name="search" class="form-control"
                                style="border-top-right-radius: 0 !important;border-bottom-right-radius: 0 !important;border-radius: 3px;border-right: none;">
                            <div class="btn btn-secondary" style="background-color: transparent;"><img
                                    src="/static/images/search.svg" height="30" alt="S" loading="lazy"
                                    class="rounded-circle"></div>
                        </div>
                    </div>

                    <div v-else>
                        <a id="" class="nav-link px-1" @click="goto('/users')" v-if="this.$store.state.login">
                            <img class="ml-2 mb-0 " src="/static/images/group.svg" height="35" alt="Community"
                                loading="lazy" />
                            <span id="" class="text-white">Connect With Users</span>
                        </a>
                    </div>
                    <div class="d-flex align-items-center px-1 mt-0 mb-0" v-if="this.$store.state.login">
                        <div class="collapse navbar-collapse" id="navbarSupportedContent">
                            <ul class="navbar-nav me-auto mb-2 mb-lg-0 ">
                                <div class="dropdown">
                                    <button class="btn dropdown-toggle" type="button" id="drop1"
                                        data-bs-toggle="dropdown" aria-expanded="false" style="
                    padding-top: 1px;
                    padding-bottom: 1px;
                    padding-left: 3px;
                    padding-right: 3px;
                    color: #fff;
                    display: flex;
                    flex-direction: row;
                    ">
                                        <img class="profile-pic" :src="getImgUrl()" width="32" height="32"
                                            style="object-fit: cover; object-position: center top" loading="lazy">
                                        {{ this.$store.state.user.username }}
                                    </button>
                                    <ul class="dropdown-menu dropdown-menu-lg-end" aria-labelledby="drop1">
                                        <li><a class="dropdown-item hand" @click="goto('/profile/'+username)">My
                                                Profile</a></li>
                                        <li><a class="dropdown-item hand" @click="goto('/dashboard')">Dashboard</a></li>
                                        <li><a class="dropdown-item hand" @click="logout()">Logout</a></li>
                                    </ul>
                                </div>
                            </ul>
                        </div>

                    </div>



                    <div class="d-flex align-items-center" v-else>
                        <a style="text-decoration: none" class=" btn btn-dark px-3 me-2" @click="goto('/login')"">Login</a>
                        <a class=" btn btn-outline-light me-3" @click="goto('/register')">Sign up</a>
                    </div>



                    </ul>
            </div>
        </div>
    </nav>
</div>
  
  `,

  data() {
    return {
      search: "Search",
      query: "",
      x: 0,
      username: null,
      img: null,
    };
  },
  computed: {
    route() {
      this.x;
      if (this.$router.history.current.path === "/users") {
        return "Search User";
      } else if (this.$router.history.current.path === "/profile") {
        return "Search My Posts";
      } else {
        return "Search Feed";
      }
    },
  },
  methods: {
    r() {
      console.log("ggg");
      this.query = null;
      this.$store.state.query = null;
      this.$store.searchtype = null;
      // this.$store.commit("reset_search")
    },
    getImgUrl() {
      var x = this.$store.state.user.profile_pic;

      return "/static/images/user_pic/" + x;
    },
    goto(url) {
      this.$router.push(url).catch(() => {});
    },
    sear() {
      if (this.query.length == 0) {
        this.$store.state.searchtype = null;
        this.$store.state.query = null;
      }
      if (this.query.length >= 0) {
        this.$store.commit("search", this.query);
      }
    },
    logout() {
      this.$store.commit("set_login_details", false);
      fetch(`/logou`, {
        headers: {
          Authorization: `Bearer ${
            sessionStorage.getItem("access_token")
              ? sessionStorage.getItem("access_token")
              : localStorage.getItem("access_token")
          }`,
        },
      })
        .then((r) => r.json())
        .then((d) => {
          console.log(d.msg);
        });
      this.$store.state.user = {};
      this.$router.push("/");
      localStorage.removeItem("access_token");
      sessionStorage.removeItem("access_token");
    },
    login() {
      fetch("/log", {
        method: "POST",
        body: JSON.stringify({
          username: this.username,
          password: this.password,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((res) => {
          if (res.ok) {
            return res.json();
          }
        })
        .then((data) => {
          localStorage.setItem("auth-token", data.auth);
          this.$router.push("/");
        });
    },
  },
  watch: {
    $route(to, from) {
      this.x++;
    },
    query(n, o) {
      if (n >= 0) {
        this.$store.commit("search", n);
      }
      console.log("Navbar: ", n);
      this.$store.state.query = n;
      console.log("store: ", this.$store.state.query);
    },
  },
  async mounted() {
    if (this.$store.state.login) {
      console.log("fetch user");
      // context.commit("set_user_details", {})
      try {
        const response = await fetch("/current-user", {
          headers: {
            Authorization: `Bearer ${
              sessionStorage.getItem("access_token")
                ? sessionStorage.getItem("access_token")
                : localStorage.getItem("access_token")
            }`,
          },
        });
        const jsonData = await response.json();
        this.username = jsonData.username;
        this.$store.state.user = jsonData;
        console.log(jsonData.username);
      } catch (error) {
        console.error(error);
      }
    }
  },
};
