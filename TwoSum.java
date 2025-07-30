class TwoSum {
    public int[] twoSum(int[] nums, int target) {
Map<Integer,Integer> map =new HashMap<>();
for(int i=0;i<nums.length;i++){
    int sums= target-nums[i];
    if(map.containsKey(sums)){
        return new int[]{map.get(sums),i};
    }
    map.put(nums[i],i);
}
return null;
    }
}