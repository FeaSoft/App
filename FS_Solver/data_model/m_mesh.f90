! Description:
! Definition of a finite element mesh.
module m_mesh
    use m_node
    use m_element
    implicit none
    
    private
    public t_mesh, new_mesh
    
    type t_mesh
        integer                      :: n_nodes     ! number of nodes
        integer                      :: n_elements  ! number of elements
        integer                      :: m_space     ! modeling space
        type(t_node),    allocatable :: nodes(:)    ! mesh nodes
        type(t_element), allocatable :: elements(:) ! mesh elements
        integer,         allocatable :: e_counts(:) ! number of elements connected to each node
    contains
        procedure :: count_elements_per_node
        final     :: destructor
    end type
    
    interface new_mesh
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Finite element mesh constructor.
    type(t_mesh) function constructor(n_nodes, n_elements, m_space) result(this)
        integer, intent(in) :: n_nodes    ! number of nodes
        integer, intent(in) :: n_elements ! number of elements
        integer, intent(in) :: m_space    ! modeling space
        this%n_nodes    = n_nodes
        this%n_elements = n_elements
        this%m_space    = m_space
        allocate(this%nodes(this%n_nodes))
        allocate(this%elements(this%n_elements))
        allocate(this%e_counts(this%n_nodes))
    end function
    
    ! Description:
    ! Finite element mesh destructor.
    subroutine destructor(this)
        type(t_mesh), intent(inout) :: this
        if (allocated(this%nodes))    deallocate(this%nodes)
        if (allocated(this%elements)) deallocate(this%elements)
        if (allocated(this%e_counts)) deallocate(this%e_counts)
    end subroutine
    
    ! Description:
    ! Counts the number of elements connected to each node.
    subroutine count_elements_per_node(this)
        class(t_mesh), intent(inout) :: this
        integer :: i, j
        
        ! count elements per node
        do i = 1, this%n_elements
            do j = 1, this%elements(i)%n_nodes
                this%e_counts(this%elements(i)%i_nodes(j)) = this%e_counts(this%elements(i)%i_nodes(j)) + 1
            end do
        end do
    end subroutine
    
end module
