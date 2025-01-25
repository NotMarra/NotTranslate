<script>
	let { children } = $props();
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
    import { Button } from "$lib/components/ui/button";
    import { page } from '$app/state';

    const sites = ["Dashboard", "Statistics", "Translate", "Translations", "Settings"];
</script>
<div class="flex">
    <nav class="h-screen fixed w-[200px] p-1 transition-all duration-5 bg-neutral-900 text-white text-center">
    <h1 class="text-3xl font-bold mt-3">NotTranslate</h1>
        <ul class="mt-20">
          {#each sites as site}
          <!--
            {#if site == "Settings"}
              <a href="/settings"><li class="w-full p-3 mt-2 text-center uppercase font-bold hover:bg-neutral-800 duration-200 rounded-lg">{site}</li></a>
            {:else}
          -->
              {#if page.route.id?.toLowerCase().split("/")[page.route.id?.toLowerCase().split("/").length - 1] == site.toLowerCase()}
                <li class="w-full p-3 text-center uppercase font-bold hover:bg-blue-800 duration-200 bg-blue-700 rounded-lg">{site}</li>
              {:else}
                <a href="/dashboard/{site.toLowerCase()}"><li class="w-full p-3 mt-2 text-center uppercase font-bold hover:bg-neutral-800 duration-200 rounded-lg">{site}</li></a>
              {/if}
          {/each}
        </ul>
      </nav>
    <div class="ml-[200px] w-full">
      <header class="flex justify-end w-full p-10 h-20 items-center bg-neutral-900 text-white shadow-lg">
          <DropdownMenu.Root>
              <DropdownMenu.Trigger><Button class="bg-white hover:bg-neutral-200 text-black">Account</Button></DropdownMenu.Trigger>
              <DropdownMenu.Content>
                <DropdownMenu.Group>
                  <DropdownMenu.Label>My Account</DropdownMenu.Label>
                  <DropdownMenu.Separator />
                  <DropdownMenu.Item>Profile</DropdownMenu.Item>
                  <DropdownMenu.Item>Billing</DropdownMenu.Item>
                  <DropdownMenu.Item>Team</DropdownMenu.Item>
                  <DropdownMenu.Item>Subscription</DropdownMenu.Item>
                </DropdownMenu.Group>
              </DropdownMenu.Content>
          </DropdownMenu.Root>
    </header>
      {@render children()}
    </div>
</div>