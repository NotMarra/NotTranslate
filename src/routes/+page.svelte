<script lang="ts">
	import { Button } from '$lib/components/ui/button';
</script>

<main class="h-full text-white bg-black -z-20 relative">
	<div class="absolute w-full overflow-hidden h-[100vh] flex justify-center -z-10">
		<div
			class="w-[80%] h-[125vh] blur-2xl bg-gradient-radial from-sky-600 via-transparent opacity-50 to-transparent absolute -top-1/2 mx-auto"
		></div>
		<div
			class="w-[110vw] h-[150vh] blur-2xl bg-gradient-radial from-sky-700 via-transparent opacity-25 to-transparent absolute -top-1/2 mx-auto"
		></div>
	</div>
	<!-- radial gradient -->
	<header class="flex justify-between p-10 h-20 items-center">
		<h1 class="text-3xl font-bold">NotTranslate</h1>
		<Button class="bg-white text-black">Sign in</Button>
	</header>

	<section class="flex justify-around w-full p-20 mt-20">
		<div>
			<h2 class="text-5xl">AI-Powered Subtitle Translation</h2>
			<p class="text-lg mt-10 w-3/4">
				NotTranslate uses cutting edge AI to translate your subtitles quickly and accurately,
				supporting ASS format and more.
			</p>
		</div>
		<img src="https://placehold.co/200x200" alt="" />
	</section>
	<div class="place-self-center w-100% flex gap-5 mt-10 mb-10">
		<Button class="bg-white text-black hover:bg-white">Start for free</Button>
		<Button variant="outline" class="bg-black">Learn more</Button>
	</div>
	<section class="flex flex-col w-full p-20 mt-20">
		<h2 class="text-5xl self-center">AI-Driven features</h2>
		<div class="flex justify-center gap-10 mt-20 w-full">
			<div
				class="border-2 border-notmarra_primary p-10 rounded-2xl flex flex-col items-center min-h-[450px] w-[350px] shadow-md shadow-notmarra_primary relative overflow-hidden"
			>
				<div
					class="absolute inset-0 blur-2xl size-96 bg-gradient-radial from-notmarra_primary via-transparent to-transparent -top-1/3 opacity-40"
				></div>
				<div class="z-10 w-full flex flex-col items-center">
					<img class="" src="https://placehold.co/150x150" alt="" srcset="" />
					<h3 class="text-4xl mt-5">Header</h3>
					<p class="mt-10">Lorem ipsum dolor sit amet consectetur adipisicing elit.</p>
				</div>
			</div>

			<div
				class="border-2 border-blue-500 p-10 rounded-2xl flex flex-col items-center min-h-[450px] w-[350px]"
			>
				<img class="" src="https://placehold.co/150x150" alt="" srcset="" />
				<h3 class="text-4xl mt-5">Header</h3>
				<p class="mt-10">Lorem ipsum dolor sit amet consectetur adipisicing elit.</p>
			</div>

			<div
				class="border-2 border-blue-500 p-10 rounded-2xl flex flex-col items-center min-h-[450px] w-[350px]"
			>
				<img class="" src="https://placehold.co/150x150" alt="" srcset="" />
				<h3 class="text-4xl mt-5">Header</h3>
				<p class="mt-10">Lorem ipsum dolor sit amet consectetur adipisicing elit.</p>
			</div>
		</div>
	</section>

	<section class="flex flex-col w-full p-20 mt-10">
		<h2 class="text-5xl self-center">Pricing plans</h2>
		<div class="flex justify-center gap-10 mt-20 w-full">
			<div class="border-2 border-blue-500 p-10 rounded-2xl flex flex-col min-h-[450px] w-[350px]">
				<h3 class="text-5xl self-center">Basic</h3>
				<h2 class="text-3xl mt-5 self-center">$0 / month</h2>
				<ul class="mt-5 list-disc list-inside">
					<li class="leading-loose">Lorem, ipsum.</li>
					<li class="leading-loose">Soluta, voluptate?</li>
					<li class="leading-loose">Labore, debitis!</li>
					<li class="leading-loose">Impedit, ipsum.</li>
					<li class="leading-loose">Debitis, provident.</li>
				</ul>
				<Button variant="outline" class="bg-black text-white hover:bg-white mt-10">Buy plan</Button>
			</div>

			<div class="border-2 border-blue-500 p-10 rounded-2xl flex flex-col min-h-[450px] w-[350px]">
				<h3 class="text-5xl self-center">Premium</h3>
				<h2 class="text-3xl mt-5 self-center">$15 / month</h2>
				<ul class="mt-5 list-disc list-inside">
					<li class="leading-loose">Lorem, ipsum.</li>
					<li class="leading-loose">Soluta, voluptate?</li>
					<li class="leading-loose">Labore, debitis!</li>
					<li class="leading-loose">Impedit, ipsum.</li>
					<li class="leading-loose">Debitis, provident.</li>
				</ul>
				<Button variant="outline" class="bg-black text-white hover:bg-white mt-10">Buy plan</Button>
			</div>

			<div class="border-2 border-blue-500 p-10 rounded-2xl flex flex-col min-h-[450px] w-[350px]">
				<h3 class="text-5xl self-center">Custom</h3>
				<h2 class="text-3xl mt-5 self-center">500$ / month</h2>
				<ul class="mt-5 list-disc list-inside">
					<li class="leading-loose">Lorem, ipsum.</li>
					<li class="leading-loose">Soluta, voluptate?</li>
					<li class="leading-loose">Labore, debitis!</li>
					<li class="leading-loose">Impedit, ipsum.</li>
					<li class="leading-loose">Debitis, provident.</li>
				</ul>
				<Button variant="outline" class="bg-black text-white hover:bg-white mt-10">Buy plan</Button>
			</div>
		</div>
	</section>
</main>
